import { Connection, Keypair } from "@solana/web3.js";
import { bs58 } from "@coral-xyz/anchor/dist/cjs/utils/bytes";
import dotenv from "dotenv";

dotenv.config();

// Wallet Configuration
export const user = Keypair.fromSecretKey(
  new Uint8Array(bs58.decode(process.env.PRIVATE_KEY || ""))
);

// Network Configuration
export const RPC = process.env.RPC || "https://mainnet.helius-rpc.com/?api-key=6bfdc1b2-fa33-4bab-be75-40f1b049df64";
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
