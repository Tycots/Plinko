from algopy import (
    Account,
    ARC4Contract,
    arc4,
    Bytes,
    Global,
    gtxn,
    itxn,
    LocalState,
    GlobalState,
    op,
    Txn,
    UInt64,
    subroutine,
)

class BettingContract(ARC4Contract):
    def __init__(self) -> None:
        self.house = GlobalState(Account, key=b"house")
        self.total_bets = GlobalState(UInt64, key=b"totalBets")
        self.total_payout = GlobalState(UInt64, key=b"totalPayout")
        self.min_bet = GlobalState(UInt64, key=b"minBet")
        self.max_bet = GlobalState(UInt64, key=b"maxBet")
        self.house_fee_bps = GlobalState(UInt64, key=b"houseFeeBps")

        self.pending_bet_round = LocalState(UInt64, key=b"pRound")
        self.pending_bet_amount = LocalState(UInt64, key=b"pAmt")
        self.pending_risk = LocalState(UInt64, key=b"pRisk")

    @arc4.abimethod(allow_actions=["NoOp"])
    def create_application(self) -> None:
        self.house.value = Account("6VUNCQFJRBVIEVHUSNXELX7NJPYTQJ2FUAYXD6DSPX3BK2A57X4JCYXEH4")
        self.total_bets.value = UInt64(0)
        self.total_payout.value = UInt64(0)
        self.min_bet.value = UInt64(100_000)
        self.max_bet.value = UInt64(100_000_000)
        self.house_fee_bps.value = UInt64(300)

    @arc4.abimethod(allow_actions=["OptIn"])
    def opt_in(self) -> None:
        self.pending_bet_round[Txn.sender] = UInt64(0)
        self.pending_bet_amount[Txn.sender] = UInt64(0)
        self.pending_risk[Txn.sender] = UInt64(0)

    @arc4.abimethod
    def submit_bet(self, pay: gtxn.PaymentTransaction, risk_level: UInt64) -> None:
        assert pay.receiver == Global.current_application_address, "Wrong receiver"
        assert self.pending_bet_round[Txn.sender] == 0, "Already have a bet pending"
        assert pay.amount >= self.min_bet.value, "Bet below minimum"
        assert pay.amount <= self.max_bet.value, "Bet exceeds maximum"
        assert risk_level <= UInt64(2), "Invalid risk level"
        
        self.pending_bet_round[Txn.sender] = Global.round + 1
        self.pending_bet_amount[Txn.sender] = pay.amount
        self.pending_risk[Txn.sender] = risk_level

    @arc4.abimethod
    def settle_bet(self) -> None:
        target_round = self.pending_bet_round[Txn.sender]
        bet_amount = self.pending_bet_amount[Txn.sender]

        assert target_round > 0, "No bet pending"
        assert Global.round > target_round, "Wait for next block"

        block_seed = op.Block.blk_seed(target_round)
        seed = op.sha256(block_seed + Txn.sender.bytes)

        # 16 rows means 17 buckets (indices 0 to 16)
        num_buckets = UInt64(17) 
        bucket_index = op.btoi(op.extract(seed, 0, 8)) % num_buckets

        half = num_buckets // 2
        pos = bucket_index
        if bucket_index > half:
            pos = UInt64(16) - bucket_index

        risk = self.pending_risk[Txn.sender]
        multiplier = UInt64(0)
        
        if risk == UInt64(0):
            multiplier = _get_low_risk(pos)
        elif risk == UInt64(1):
            multiplier = _get_mid_risk(pos)
        else:
            multiplier = _get_high_risk(pos)

        house_fee = (bet_amount * self.house_fee_bps.value) // 10_000
        final_payout = ((bet_amount - house_fee) * multiplier) // 100

        if house_fee > 0:
            itxn.Payment(receiver=self.house.value, amount=house_fee).submit()
        
        if final_payout > 0:
            itxn.Payment(receiver=Txn.sender, amount=final_payout).submit()

        self.total_bets.value += 1
        self.total_payout.value += final_payout
        self.pending_bet_round[Txn.sender] = UInt64(0)
        self.pending_bet_amount[Txn.sender] = UInt64(0)

    @arc4.abimethod
    def refund_bet(self, player: Account) -> None:
        target_round = self.pending_bet_round[player]
        amount = self.pending_bet_amount[player]
        assert target_round > 0, "No bet"
        itxn.Payment(receiver=player, amount=amount).submit()
        self.pending_bet_round[player] = UInt64(0)
        self.pending_bet_amount[player] = UInt64(0)

    @arc4.abimethod
    def withdraw(self, amount: UInt64) -> None:
        assert Txn.sender == self.house.value, "Not house"
        itxn.Payment(receiver=self.house.value, amount=amount).submit()


@subroutine
def _get_low_risk(pos: UInt64) -> UInt64:
    if pos == UInt64(0):
        return UInt64(150)
    if pos == UInt64(1):
        return UInt64(102)
    if pos == UInt64(2):
        return UInt64(100)
    if pos == UInt64(3):
        return UInt64(98)
    if pos == UInt64(4):
        return UInt64(96)
    if pos == UInt64(5):
        return UInt64(94)
    if pos == UInt64(6):
        return UInt64(92)
    if pos == UInt64(7):
        return UInt64(90)
    return UInt64(88)


@subroutine
def _get_mid_risk(pos: UInt64) -> UInt64:
    if pos == UInt64(0):
        return UInt64(300)
    if pos == UInt64(1):
        return UInt64(150)
    if pos == UInt64(2):
        return UInt64(125)
    if pos == UInt64(3):
        return UInt64(80)
    if pos == UInt64(4):
        return UInt64(58)
    if pos == UInt64(5):
        return UInt64(48)
    if pos == UInt64(6):
        return UInt64(38)
    if pos == UInt64(7):
        return UInt64(28)
    return UInt64(25)


@subroutine
def _get_high_risk(pos: UInt64) -> UInt64:
    if pos == UInt64(0):
        return UInt64(600)
    if pos == UInt64(1):
        return UInt64(150)
    if pos == UInt64(2):
        return UInt64(42)
    if pos == UInt64(3):
        return UInt64(20)
    if pos == UInt64(4):
        return UInt64(10)
    if pos == UInt64(5):
        return UInt64(5)
    if pos == UInt64(6):
        return UInt64(3)
    if pos == UInt64(7):
        return UInt64(2)
    return UInt64(1)