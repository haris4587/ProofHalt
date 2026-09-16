// SPDX-License-Identifier: MIT
pragma solidity 0.8.36;

/// @notice Minimal interface a ProofHalt-protected target must expose.
interface IProofHaltProtected {
    function proofHaltPause() external;
    function proofHaltRestore() external;
    function paused() external view returns (bool);
    function proofHaltGuardian() external view returns (address);
}

/// @title ProofHaltGuardian
/// @notice Narrow EVM-side authority bridge for finalized ProofHalt decisions.
/// @dev The GenLayer Intelligent Contract's ghost contract shares the IC address,
///      so finalized external messages arrive with msg.sender == proofHaltAuthority.
contract ProofHaltGuardian {
    uint8 private constant ACTION_HALT = 1;
    uint8 private constant ACTION_RESTORE = 2;

    address public immutable proofHaltAuthority;
    address public immutable protectedTarget;

    /// @notice Number of incidents that currently require the target to remain paused.
    uint256 public activeHaltCount;

    struct IncidentState {
        uint32 latestRevision;
        bytes32 decisionBinding;
        bool haltActive;
        bool everHalted;
        bool restored;
    }

    mapping(bytes32 incidentHash => IncidentState state) private _incidentStates;
    mapping(bytes32 actionKey => bool executed) private _executedActions;

    error UnauthorizedCaller(address caller);
    error ZeroAddress();
    error TargetNotContract(address target);
    error InvariantViolation();
    error InvalidIncidentId();
    error InvalidRevision();
    error InvalidDecisionBinding();
    error StaleRevision(uint32 supplied, uint32 latest);
    error ConflictingRevision(uint32 revision);
    error IncidentNotActive(bytes32 incidentHash);
    error IncidentAlreadyRestored(bytes32 incidentHash);
    error TargetNotBound(address expectedGuardian, address actualGuardian);
    error TargetStateInconsistent(bool paused, uint256 activeHalts);
    error TargetStateChangeFailed(bool expectedPaused, bool actualPaused);

    event HaltActivated(
        bytes32 indexed incidentHash,
        string incidentId,
        uint32 indexed revision,
        bytes32 decisionBinding,
        uint256 activeHaltCount
    );

    event RestoreActivated(
        bytes32 indexed incidentHash,
        string incidentId,
        uint32 indexed revision,
        bytes32 decisionBinding,
        uint256 activeHaltCount,
        bool targetRestored
    );

    event ReplayIgnored(
        bytes32 indexed incidentHash,
        uint32 indexed revision,
        uint8 indexed action
    );

    constructor(address proofHaltAuthority_, address protectedTarget_) {
        if (proofHaltAuthority_ == address(0) || protectedTarget_ == address(0)) {
            revert ZeroAddress();
        }
        if (protectedTarget_.code.length == 0) {
            revert TargetNotContract(protectedTarget_);
        }
        proofHaltAuthority = proofHaltAuthority_;
        protectedTarget = protectedTarget_;
    }

    modifier onlyProofHalt() {
        if (msg.sender != proofHaltAuthority) {
            revert UnauthorizedCaller(msg.sender);
        }
        _;
    }

    /// @notice Returns the target's real pause state.
    /// @dev Also acts as an end-to-end binding check during ProofHalt activation.
    function isPaused() external view returns (bool) {
        _requireTargetBound();
        return IProofHaltProtected(protectedTarget).paused();
    }

    /// @notice Apply a finalized HALT authorization from ProofHalt.
    /// @dev Exact duplicate actions are harmlessly ignored. A target remains paused
    ///      until every independently active halt incident has been restored.
    function pauseFromProofHalt(
        string calldata incidentId,
        uint32 revision,
        bytes calldata decisionBinding
    ) external onlyProofHalt {
        bytes32 incidentHash = _validateAndHashIncident(incidentId, revision);
        bytes32 binding = _validateDecisionBinding(decisionBinding);
        bytes32 actionKey = _actionKey(incidentHash, revision, ACTION_HALT, binding);

        if (_executedActions[actionKey]) {
            emit ReplayIgnored(incidentHash, revision, ACTION_HALT);
            return;
        }

        _requireTargetBound();

        IncidentState storage state = _incidentStates[incidentHash];
        if (state.restored) {
            revert IncidentAlreadyRestored(incidentHash);
        }
        _requireFreshRevision(state.latestRevision, revision);

        bool targetPausedBefore = IProofHaltProtected(protectedTarget).paused();
        _requireConsistentTargetState(targetPausedBefore);

        _executedActions[actionKey] = true;
        state.latestRevision = revision;
        state.decisionBinding = binding;
        state.everHalted = true;

        if (!state.haltActive) {
            state.haltActive = true;
            activeHaltCount += 1;
        }

        if (!targetPausedBefore) {
            IProofHaltProtected(protectedTarget).proofHaltPause();
            bool targetPausedAfter = IProofHaltProtected(protectedTarget).paused();
            if (!targetPausedAfter) {
                revert TargetStateChangeFailed(true, targetPausedAfter);
            }
        }

        emit HaltActivated(incidentHash, incidentId, revision, binding, activeHaltCount);
    }

    /// @notice Apply a finalized RESTORE authorization from ProofHalt.
    /// @dev Resolves only this incident's halt. The protected target is unpaused only
    ///      when no other active ProofHalt incident still requires a halt.
    function restoreFromProofHalt(
        string calldata incidentId,
        uint32 revision,
        bytes calldata decisionBinding
    ) external onlyProofHalt {
        bytes32 incidentHash = _validateAndHashIncident(incidentId, revision);
        bytes32 binding = _validateDecisionBinding(decisionBinding);
        bytes32 actionKey = _actionKey(incidentHash, revision, ACTION_RESTORE, binding);

        if (_executedActions[actionKey]) {
            emit ReplayIgnored(incidentHash, revision, ACTION_RESTORE);
            return;
        }

        _requireTargetBound();

        IncidentState storage state = _incidentStates[incidentHash];
        if (!state.haltActive) {
            revert IncidentNotActive(incidentHash);
        }
        _requireFreshRevision(state.latestRevision, revision);

        bool targetPausedBefore = IProofHaltProtected(protectedTarget).paused();
        _requireConsistentTargetState(targetPausedBefore);

        _executedActions[actionKey] = true;
        state.latestRevision = revision;
        state.decisionBinding = binding;
        state.haltActive = false;
        state.restored = true;

        // A live incident must correspond to at least one active halt globally.
        // Fail with an explicit invariant error rather than relying on arithmetic panic.
        if (activeHaltCount == 0) revert InvariantViolation();
        activeHaltCount -= 1;

        bool targetRestored = false;
        if (activeHaltCount == 0) {
            IProofHaltProtected(protectedTarget).proofHaltRestore();
            bool targetPausedAfter = IProofHaltProtected(protectedTarget).paused();
            if (targetPausedAfter) {
                revert TargetStateChangeFailed(false, targetPausedAfter);
            }
            targetRestored = true;
        } else {
            // Resolving one incident must never unpause while another halt remains.
            bool targetPausedAfter = IProofHaltProtected(protectedTarget).paused();
            if (!targetPausedAfter) {
                revert TargetStateChangeFailed(true, targetPausedAfter);
            }
        }

        emit RestoreActivated(
            incidentHash,
            incidentId,
            revision,
            binding,
            activeHaltCount,
            targetRestored
        );
    }

    /// @notice True only while this specific incident currently contributes to the halt.
    function isIncidentActive(string calldata incidentId) external view returns (bool) {
        return _incidentStates[keccak256(bytes(incidentId))].haltActive;
    }

    /// @notice True after this specific incident has received a finalized restore.
    function isIncidentRestored(string calldata incidentId) external view returns (bool) {
        return _incidentStates[keccak256(bytes(incidentId))].restored;
    }

    /// @notice Latest ProofHalt verdict commitment applied for this incident.
    function incidentDecisionBinding(string calldata incidentId) external view returns (bytes memory) {
        return abi.encodePacked(_incidentStates[keccak256(bytes(incidentId))].decisionBinding);
    }

    function incidentState(
        string calldata incidentId
    ) external view returns (
        uint32 latestRevision,
        bytes32 decisionBinding,
        bool haltActive,
        bool everHalted,
        bool restored
    ) {
        bytes32 incidentHash = keccak256(bytes(incidentId));
        IncidentState storage state = _incidentStates[incidentHash];
        return (
            state.latestRevision,
            state.decisionBinding,
            state.haltActive,
            state.everHalted,
            state.restored
        );
    }

    function actionExecuted(
        string calldata incidentId,
        uint32 revision,
        bool restoreAction,
        bytes calldata decisionBinding
    ) external view returns (bool) {
        bytes32 incidentHash = keccak256(bytes(incidentId));
        uint8 action = restoreAction ? ACTION_RESTORE : ACTION_HALT;
        bytes32 binding = _validateDecisionBinding(decisionBinding);
        return _executedActions[_actionKey(
            incidentHash,
            revision,
            action,
            binding
        )];
    }

    function incidentHashOf(string calldata incidentId) external pure returns (bytes32) {
        return keccak256(bytes(incidentId));
    }

    function _validateAndHashIncident(
        string calldata incidentId,
        uint32 revision
    ) private pure returns (bytes32 incidentHash) {
        if (bytes(incidentId).length == 0) revert InvalidIncidentId();
        if (revision == 0) revert InvalidRevision();
        return keccak256(bytes(incidentId));
    }

    function _requireFreshRevision(uint32 latestRevision, uint32 supplied) private pure {
        if (supplied < latestRevision) {
            revert StaleRevision(supplied, latestRevision);
        }
        if (latestRevision != 0 && supplied == latestRevision) {
            revert ConflictingRevision(supplied);
        }
    }

    function _validateDecisionBinding(bytes calldata supplied) private pure returns (bytes32) {
        if (supplied.length != 32) revert InvalidDecisionBinding();
        return abi.decode(supplied, (bytes32));
    }

    function _requireTargetBound() private view {
        address actualGuardian = IProofHaltProtected(protectedTarget).proofHaltGuardian();
        if (actualGuardian != address(this)) {
            revert TargetNotBound(address(this), actualGuardian);
        }
    }

    function _requireConsistentTargetState(bool targetPaused) private view {
        // Demo/protected target starts unpaused. There must be a one-to-one relation
        // between "at least one active halt" and the target's paused state.
        bool shouldBePaused = activeHaltCount > 0;
        if (targetPaused != shouldBePaused) {
            revert TargetStateInconsistent(targetPaused, activeHaltCount);
        }
    }

    function _actionKey(
        bytes32 incidentHash,
        uint32 revision,
        uint8 action,
        bytes32 decisionBinding
    ) private pure returns (bytes32) {
        return keccak256(
            abi.encode(
                keccak256("PROOFHALT_GUARDIAN_ACTION_V2"),
                incidentHash,
                revision,
                action,
                decisionBinding
            )
        );
    }
}
