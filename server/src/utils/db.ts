import fs from 'fs';
import path from 'path';

export const saveInvestedPool = async (poolAddress: string, amount: number) => {
    const filePath = path.join(__dirname, '..', 'data', 'investedPools.json');
    const data = fs.readFileSync(filePath, 'utf8');
    const jsonData = JSON.parse(data);
    jsonData.push({ poolAddress, amount });
    fs.writeFileSync(filePath, JSON.stringify(jsonData, null, 2));
}

export const get_investments = async () => {
    const filePath = path.join(__dirname, '..', 'data', 'investedPools.json');
    const data = fs.readFileSync(filePath, 'utf8');
    return JSON.parse(data);
}

export const removeInvestment = async (poolAddress: string) => {
    const filePath = path.join(__dirname, '..', 'data', 'investedPools.json');
    const data = fs.readFileSync(filePath, 'utf8');
    const jsonData = JSON.parse(data);
    const newData = jsonData.filter((pool: { poolAddress: string }) => pool.poolAddress !== poolAddress);
    fs.writeFileSync(filePath, JSON.stringify(newData, null, 2));
}

export const addLiquidityToExistingPool = async (poolAddress: string, amount: number) => {
    const filePath = path.join(__dirname, '..', 'data', 'investedPools.json');
    const data = fs.readFileSync(filePath, 'utf8');
    const jsonData = JSON.parse(data);
    const pool = jsonData.find((pool: { poolAddress: string }) => pool.poolAddress === poolAddress);
    if (pool) {
        pool.amount += amount;
    }
    fs.writeFileSync(filePath, JSON.stringify(jsonData, null, 2));
}