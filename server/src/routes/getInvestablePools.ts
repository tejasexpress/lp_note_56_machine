import { Router } from 'express';
import path from 'path';
import fs from 'fs';



const router = Router();

const getPairs = router.get('/getPairs', async (req, res) => {
    const dataFilePath = path.join(__dirname, '../../../data/investable_pairs.json');
    const investable_pools = fs.readFileSync(dataFilePath, 'utf-8');
    res.status(200).json(JSON.parse(investable_pools));
});

export default getPairs;