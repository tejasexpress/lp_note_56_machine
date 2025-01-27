import { Router } from 'express';
import { PublicKey } from "@solana/web3.js";
import {connection} from '../utils/config'
import DLMM from '@meteora-ag/dlmm';
import { manageRisk } from '../utils/dlmmOperations';

const router = Router();

const createPosition = router.post('/update', async (req, res) => {
  try {
    const { poolAddress } = req.body;
    const poolPubkey = new PublicKey(poolAddress);
    const dlmmPool = await DLMM.create(connection, poolPubkey);
    await manageRisk(dlmmPool);
    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

export default createPosition;