import { Router } from 'express';
import { PublicKey } from "@solana/web3.js";
import {connection, user} from '../utils/config'
import DLMM from '@meteora-ag/dlmm';
import { createBalancePosition, getUserPositions } from '../utils/dlmmOperations';
import { addInvestedPool } from '../utils/db';

const router = Router();

const createPosition = router.post('/', async (req, res) => {
  try {
    const { poolAddress, amount } = req.body;
    const poolPubkey = new PublicKey(poolAddress);
    
    const dlmmPool = await DLMM.create(connection, poolPubkey, {
      "cluster": "mainnet-beta",
    });

    console.log(dlmmPool);

    const err = await createBalancePosition(dlmmPool, Number(amount));
    if(err === null) {
      await addInvestedPool(poolAddress, amount)
    }
    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

export default createPosition;