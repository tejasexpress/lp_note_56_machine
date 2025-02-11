import { Router } from 'express';
import {connection, user} from '../utils/config'
import DLMM from '@meteora-ag/dlmm';
import { mapToJson } from '../utils/utils';


const router = Router();

const getPos = router.get('/getPos', async (req, res) => {
    try {
        const positions = await DLMM.getAllLbPairPositionsByUser(connection, user.publicKey);
       
        res.status(200).json(await mapToJson(positions));

    } catch (error) {
        res.status(500).json({ error: (error as Error).message });
    }
});

export default getPos;