import { Router } from 'express';
import { PublicKey } from "@solana/web3.js";
import {connection, user} from '../utils/config'
import DLMM from '@meteora-ag/dlmm';
import { claimFees } from '../utils/dlmmOperations';
import { addInvestedPool } from '../utils/db';

const router = Router();

const claimFee = router.post('/claim', async (req, res) => {
  try {
    const { poolAddress, positionPubKey } = req.body;
    const poolPubkey = new PublicKey(poolAddress);
    
    const dlmmPool = await DLMM.create(connection, poolPubkey, {
      "cluster": "mainnet-beta",
    });

    
    const err = await claimFees(dlmmPool, positionPubKey);
    
    if(err == null) {
      res.status(200).json({ success: true });
    } else {
        res.status(500).json({ error: err });
    }

  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

export default claimFee;