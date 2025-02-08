import { Router } from 'express';
import { PublicKey } from "@solana/web3.js";
import {connection} from '../utils/config'
import DLMM from '@meteora-ag/dlmm';
import { removePositionLiquidity } from '../utils/dlmmOperations';

const router = Router();

const sellPosition = router.post('/', async (req, res) => {
  try {
    const { poolAddress } = req.body;
    const poolPubkey = new PublicKey(poolAddress);

    
    const dlmmPool = await DLMM.create(connection, poolPubkey, {
      "cluster": "mainnet-beta",
    });

    console.log(dlmmPool);

    await removePositionLiquidity(dlmmPool);
    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

export default sellPosition;