import { Router } from 'express';
const router = Router();
import DLMM from '@meteora-ag/dlmm';
import { PublicKey, Connection } from '@solana/web3.js';


const buy =router.post('/buy', (req, res) => {
    const address: string = req.body.address;
    const amount: number = req.body.amount;

    const POOL = new PublicKey(address);
    const dlmmPool = DLMM(Connection, POOL);
});

export default buy;
