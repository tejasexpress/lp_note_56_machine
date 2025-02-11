import { Router, json } from 'express';
import { PublicKey } from "@solana/web3.js";
import {connection, user} from '../utils/config'
import DLMM from '@meteora-ag/dlmm';
import { manageRisk } from '../utils/dlmmOperations';
import { mapToJson } from '../utils/utils';

const router = Router();

const update = router.post('/update', async (req, res) => {
  try {
    const positions = await DLMM.getAllLbPairPositionsByUser(connection, user.publicKey);

    const jsonPositions = await mapToJson(positions);

    if(positions.size > 0) {
      for(const position of positions) {
        console.log(position[1]['lbPairPositionsData']);
        break;
        // await manageRisk(position);
      }
    }
    res.status(200).json("updated positions");
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

export default update;