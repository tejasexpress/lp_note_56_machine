import fs from 'fs';
import path from 'path';

const dataFilePath = path.join(__dirname, '../../../data/invested_pools.json');

// Function to read current invested pools
const readInvestedPools = () => {
  const data = fs.readFileSync(dataFilePath, 'utf-8');
  const parsedData = JSON.parse(data);
  return parsedData.pools; // Return the pools array
};

// Function to write updated pools back to the JSON file
const writeInvestedPools = (pools: any) => {
  const dataToWrite = { pools }; // Wrap pools in an object
  fs.writeFileSync(dataFilePath, JSON.stringify(dataToWrite, null, 2), 'utf-8');
};

// Function to add a position
export const addInvestedPool = (poolAddress: string, amount: number) => {
  console.log("Transaction Successful, adding pool");
  const pools = readInvestedPools();
  pools.push({ poolAddress, amount, createdAt: new Date().toISOString() }); // Use ISO string for date
  writeInvestedPools(pools); 
};

// Function to remove a position
export const removeInvestedPool = (poolAddress: string) => {
  const pools = readInvestedPools();
  const index = pools.findIndex((pool: any) => pool.poolAddress === poolAddress);
  if (index !== -1) {
    pools.splice(index, 1); // Remove the pool if found
    writeInvestedPools(pools); // Update the JSON file
  }
};