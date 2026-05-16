# VOI Plinko Betting Contract

A fully on-chain, provably fair Plinko game deployed on the **Voi Network**.

Players choose their risk level and bet amount. The ball drops on a 16-row board and pays out based on where it lands. Everything is transparent, decentralized, and verifiable.

- Fixed **16-row** board (classic Plinko feel)
- 3 risk levels (Low / Mid / High)
- ~97% RTP across all risks (house edge ≈ 3%)
- Provably fair randomness using block seed + player address
- Example app ID 49244777
---

## Features

- Provably fair (uses `Block.blk_seed` + SHA256)
- 3% house fee (configurable)
- Minimum bet: 0.1 VOI
- Maximum bet: 100 VOI (can be lowered in `create_application`)
- Auto-refund option if bet is not settled
- House can withdraw profits

---

## Deployment Instructions

1. **Update wallet address** (Update house to own address)
2. **Deploy the contract** (create the application)
3. **Call `create_application`** once (this sets house address, fees, min/max bet, etc.)
4. **Opt-in** every player who wants to bet
5. Start accepting bets

### Important First Step After Deployment
You **must** call the `create_application` method once after deployment.  
If you don't, `submit_bet` will fail with "check self.min_bet exists".

---

## How to Play

### 1. Player Opt-in
Every player must opt-in to the app before betting.

### 2. Place a Bet (`submit_bet`)
- Send a **Payment Transaction** to the contract address
- Call `submit_bet` with:
  - `pay`: the payment transaction (must be in the same group)
  - `risk_level`: `0` = Low, `1` = Mid, `2` = High

### 3. Settle the Bet (`settle_bet`)
Anyone can call this after the next block.
The player receives their payout automatically.

### 4. Refund (if needed)
`refund_bet(player)` can be called by anyone if the bet is stuck.

---

## Risk Levels & Payouts

| Risk Level | Max Multiplier | Feel                  | Recommended For          |
|------------|----------------|-----------------------|--------------------------|
| Low (0)    | 1.08x          | Very safe             | Grinding                 |
| Mid (1)    | 2.55x          | Balanced              | Most players             |
| High (2)   | 4.35x          | Exciting              | High rollers             |

All three risks are tuned to deliver **≈97% RTP**.

---

## Contract Methods

| Method              | Type           | Description                              |
|---------------------|----------------|------------------------------------------|
| `create_application`| NoOp           | Initialize contract (call once)          |
| `opt_in`            | OptIn          | Player must opt-in                       |
| `submit_bet`        | ApplicationCall| Place a bet (with payment txn)           |
| `settle_bet`        | ApplicationCall| Settle bet and pay winner                |
| `refund_bet`        | ApplicationCall| Refund pending bet                       |
| `withdraw`          | ApplicationCall| House withdraws profits                  |

---

## Important Notes

- **Board is fixed at 16 rows** (17 buckets) – standard Plinko style.
- Randomness is based on the next block seed + player address → provably fair.
- House fee is **3%** (300 bps).
- Max bet is currently 100 VOI. You can lower it in `create_application` for safety.

---

## Liquidity Recommendation

| Max Bet | Recommended Liquidity |
|---------|-----------------------|
| 10 VOI  | 30,000 – 50,000 VOI   |
| 50 VOI  | 150,000 – 200,000 VOI |
| 100 VOI | 300,000+ VOI          |

---

## Questions?

Feel free to ask in the group chat or open an issue.

**Enjoy the game!** 🎰
