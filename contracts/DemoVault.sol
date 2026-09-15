// SPDX-License-Identifier: MIT
pragma solidity 0.8.36;

interface IProofHaltGuardianBinding {
    function proofHaltAuthority() external view returns (address);
    function protectedTarget() external view returns (address);
}

/// @title DemoVault
/// @notice TESTNET-ONLY vault used to demonstrate ProofHalt's finalized
///         EXPLOIT → PAUSE → PATCH → RESTORE lifecycle.
/// @dev INTENTIONALLY CONTAINS a bounded demo vulnerability. Never use this
///      contract to hold production funds or valuable assets.
contract DemoVault {
    address public configurationAuthority;
    address private _proofHaltGuardian;

    bool private _paused;
    bool private _guardianConfigured;
    bool private _entered;

    mapping(address account => uint256 balance) private _balances;
    uint256 public totalManagedAssets;

    /// @dev Deliberately tiny cap for the testnet-only exploit demonstration.
    uint256 public constant DEMO_MAX_EXPLOIT_PER_CALL = 1_000_000_000_000; // 0.000001 GEN
    bool public demoExploitEnabled = true;

    error UnauthorizedConfiguration(address caller);
    error UnauthorizedGuardian(address caller);
    error GuardianAlreadyConfigured();
    error InvalidGuardian();
    error GuardianTargetMismatch(address expected, address actual);
    error GuardianAuthorityMissing();
    error ProtectionNotConfigured();
    error VaultPaused();
    error ZeroDeposit();
    error InvalidAmount();
    error InsufficientBalance(uint256 available, uint256 requested);
    error TransferFailed();
    error Reentrancy();
    error DemoExploitDisabled();
    error DemoExploitAmountTooLarge(uint256 maxAllowed, uint256 requested);
    error PatchRequiresPause();
    error DemoPatchRequired();

    event GuardianConfigured(address indexed guardian, address indexed proofHaltAuthority);
    event PausedByProofHalt(address indexed guardian);
    event RestoredByProofHalt(address indexed guardian);
    event Deposited(address indexed account, uint256 amount, uint256 newBalance);
    event Withdrawn(address indexed account, uint256 amount, uint256 newBalance);
    event DemoExploitExecuted(
        address indexed attacker,
        address indexed victim,
        uint256 amount
    );
    event DemoPatchApplied(address indexed caller);

    constructor() {
        configurationAuthority = msg.sender;
    }

    modifier onlyConfigurationAuthority() {
        if (msg.sender != configurationAuthority) {
            revert UnauthorizedConfiguration(msg.sender);
        }
        _;
    }

    modifier onlyGuardian() {
        if (!_guardianConfigured) revert ProtectionNotConfigured();
        if (msg.sender != _proofHaltGuardian) {
            revert UnauthorizedGuardian(msg.sender);
        }
        _;
    }

    modifier whenNotPaused() {
        if (_paused) revert VaultPaused();
        _;
    }

    modifier nonReentrant() {
        if (_entered) revert Reentrancy();
        _entered = true;
        _;
        _entered = false;
    }

    /// @notice One-time binding to the Guardian. Configuration authority is destroyed afterward.
    function configureProofHaltGuardian(
        address guardian
    ) external onlyConfigurationAuthority {
        if (_guardianConfigured) revert GuardianAlreadyConfigured();
        if (guardian == address(0) || guardian.code.length == 0) {
            revert InvalidGuardian();
        }

        address target = IProofHaltGuardianBinding(guardian).protectedTarget();
        if (target != address(this)) {
            revert GuardianTargetMismatch(address(this), target);
        }

        address authority = IProofHaltGuardianBinding(guardian).proofHaltAuthority();
        if (authority == address(0)) revert GuardianAuthorityMissing();

        _proofHaltGuardian = guardian;
        _guardianConfigured = true;

        // Eliminate the only setup privilege after binding.
        configurationAuthority = address(0);

        emit GuardianConfigured(guardian, authority);
    }

    function proofHaltGuardian() external view returns (address) {
        return _proofHaltGuardian;
    }

    function isProofHaltConfigured() external view returns (bool) {
        return _guardianConfigured;
    }

    function paused() external view returns (bool) {
        return _paused;
    }

    /// @notice Guardian-only target action. Idempotent by design.
    function proofHaltPause() external onlyGuardian {
        if (_paused) return;
        _paused = true;
        emit PausedByProofHalt(msg.sender);
    }

    /// @notice Guardian-only target action. Idempotent by design.
    /// @dev The demo vault adds a deterministic recovery guard: the intentionally
    ///      vulnerable path must be permanently disabled before the final restore.
    function proofHaltRestore() external onlyGuardian {
        if (!_paused) return;
        if (demoExploitEnabled) revert DemoPatchRequired();
        _paused = false;
        emit RestoredByProofHalt(msg.sender);
    }

    function deposit() external payable whenNotPaused {
        _deposit(msg.sender, msg.value);
    }

    receive() external payable {
        if (_paused) revert VaultPaused();
        _deposit(msg.sender, msg.value);
    }

    /// @notice INTENTIONALLY VULNERABLE TESTNET-ONLY function.
    /// @dev Any caller can withdraw a bounded amount from another user's tracked
    ///      balance. This creates a real unauthorized-withdrawal transaction for
    ///      ProofHalt's hackathon evidence flow. The normal vault API is not vulnerable.
    function demoExploitWithdrawFrom(
        address victim,
        uint256 amount
    ) external whenNotPaused nonReentrant {
        if (!demoExploitEnabled) revert DemoExploitDisabled();
        if (amount == 0) revert InvalidAmount();
        if (amount > DEMO_MAX_EXPLOIT_PER_CALL) {
            revert DemoExploitAmountTooLarge(DEMO_MAX_EXPLOIT_PER_CALL, amount);
        }

        uint256 balance = _balances[victim];
        if (balance < amount) {
            revert InsufficientBalance(balance, amount);
        }

        _balances[victim] = balance - amount;
        totalManagedAssets -= amount;

        (bool ok, ) = payable(msg.sender).call{value: amount}("");
        if (!ok) revert TransferFailed();

        emit DemoExploitExecuted(msg.sender, victim, amount);
    }

    /// @notice Permanently disables the intentional demo vulnerability.
    /// @dev Anyone may apply this one-way safety patch, but only while the vault is
    ///      already paused. There is no method that can re-enable the vulnerability.
    function applyDemoPatch() external {
        if (!_paused) revert PatchRequiresPause();
        if (!demoExploitEnabled) return;
        demoExploitEnabled = false;
        emit DemoPatchApplied(msg.sender);
    }

    function withdraw(uint256 amount) external whenNotPaused nonReentrant {
        if (amount == 0) revert InvalidAmount();

        uint256 balance = _balances[msg.sender];
        if (balance < amount) {
            revert InsufficientBalance(balance, amount);
        }

        _balances[msg.sender] = balance - amount;
        totalManagedAssets -= amount;

        (bool ok, ) = payable(msg.sender).call{value: amount}("");
        if (!ok) revert TransferFailed();

        emit Withdrawn(msg.sender, amount, _balances[msg.sender]);
    }

    function balanceOf(address account) external view returns (uint256) {
        return _balances[account];
    }

    function _deposit(address account, uint256 amount) private {
        if (amount == 0) revert ZeroDeposit();
        _balances[account] += amount;
        totalManagedAssets += amount;
        emit Deposited(account, amount, _balances[account]);
    }
}
