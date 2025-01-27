import { Connection, Keypair } from "@solana/web3.js";
import { bs58 } from "@coral-xyz/anchor/dist/cjs/utils/bytes";

// Wallet Configuration
export const user = Keypair.fromSecretKey(
  new Uint8Array(bs58.decode(process.env.USER_PRIVATE_KEY || ""))
);

// Network Configuration
export const RPC = process.env.RPC || "https://devnet.meteora.ag";
export const connection = new Connection(RPC, "finalized");

// Risk Parameters
export const RISK_PARAMS = {
  STOP_LOSS: 0.05,
  HEALTH_SCORE_MIN: 70,
  MAX_IL: 0.015,
  VOLUME_DROP_THRESHOLD: 0.4,
  REBALANCE_DEVIATION: 0.07,
  CHECK_INTERVAL: 300000 // 5 minutes
};


export const METEORA_API_CONFIG = {
    BASE_URL: "https://api.meteora.ag",
    RATE_LIMIT: 1000, // 1 request per second
    ENDPOINTS: {
        POOL: "/pools",
        VOLUME: "/volume",
        IL: "/il"
    }
};
