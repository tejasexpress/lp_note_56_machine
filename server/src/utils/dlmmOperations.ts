import { Keypair, sendAndConfirmTransaction } from "@solana/web3.js";
import DLMM from "@meteora-ag/dlmm";
import { StrategyType } from "@meteora-ag/dlmm";
import { user, connection, RISK_PARAMS } from "./config";
import BN from "bn.js";
import axios from "axios";

export interface ParsedClockState {
	info: {
		epoch: number;
		epochStartTimestamp: number;
		leaderScheduleEpoch: number;
		slot: number;
		unixTimestamp: number;
	};
	type: string;
	program: string;
	space: number;
}


const newBalancePosition = new Keypair();

interface PoolMetrics {
	healthScore: number;
	ilRisk: number;
	volumeChange24h: number;
	currentPrice: number;
}

export async function createBalancePosition(dlmmPool: DLMM, amount: number) {
	const TOTAL_RANGE_INTERVAL = 10; // 10 bins on each side of the active bin
	const activeBin = await dlmmPool.getActiveBin();
	const minBinId = activeBin.binId - TOTAL_RANGE_INTERVAL;
	const maxBinId = activeBin.binId + TOTAL_RANGE_INTERVAL;
  
	const activeBinPricePerToken = dlmmPool.fromPricePerLamport(
	  Number(activeBin.price)
	);
	const totalXAmount = new BN(amount);
	const totalYAmount = totalXAmount.mul(new BN(Number(activeBinPricePerToken)));
  
	// Create Position
	const createPositionTx =
	  await dlmmPool.initializePositionAndAddLiquidityByStrategy({
		positionPubKey: newBalancePosition.publicKey,
		user: user.publicKey,
		totalXAmount,
		totalYAmount,
		strategy: {
		  maxBinId,
		  minBinId,
		  strategyType: StrategyType.SpotBalanced,
		},
	  });
  
	try {
	  const createBalancePositionTxHash = await sendAndConfirmTransaction(
		connection,
		createPositionTx,
		[user, newBalancePosition]
	  );
	  console.log(
		"🚀 ~ createBalancePositionTxHash:",
		createBalancePositionTxHash
	  );
	} catch (error) {
	  console.log("🚀 ~ error:", JSON.parse(JSON.stringify(error)));
	}
  }
  
  async function getUserPositions(dlmmPool: DLMM) {
	const positionsState = await dlmmPool.getPositionsByUserAndLbPair(
	  user.publicKey
	);
	return positionsState.userPositions;
  }

 
  
export async function addLiquidityToExistingPosition(dlmmPool: DLMM, amount: number) {
	const TOTAL_RANGE_INTERVAL = 10; // 10 bins on each side of the active bin
	const activeBin = await dlmmPool.getActiveBin();
	const minBinId = activeBin.binId - TOTAL_RANGE_INTERVAL;
	const maxBinId = activeBin.binId + TOTAL_RANGE_INTERVAL;
  
	const activeBinPricePerToken = dlmmPool.fromPricePerLamport(
	  Number(activeBin.price)
	);
	const totalXAmount = new BN(amount);
	const totalYAmount = totalXAmount.mul(new BN(Number(activeBinPricePerToken)));
  
	// Add Liquidity to existing position
	const addLiquidityTx = await dlmmPool.addLiquidityByStrategy({
	  positionPubKey: newBalancePosition.publicKey,
	  user: user.publicKey,
	  totalXAmount,
	  totalYAmount,
	  strategy: {
		maxBinId,
		minBinId,
		strategyType: StrategyType.SpotBalanced,
	  },
	});
  
	try {
	  const addLiquidityTxHash = await sendAndConfirmTransaction(
		connection,
		addLiquidityTx,
		[user]
	  );
	  console.log("🚀 ~ addLiquidityTxHash:", addLiquidityTxHash);
	} catch (error) {
	  console.log("🚀 ~ error:", JSON.parse(JSON.stringify(error)));
	}
}

export async function removePositionLiquidity(dlmmPool: DLMM) {
	// Remove Liquidity
	const userPositions = await getUserPositions(dlmmPool);
	const removeLiquidityTxs = (
	  await Promise.all(
		userPositions.map(({ publicKey, positionData }) => {
		  const binIdsToRemove = positionData.positionBinData.map(
			(bin) => bin.binId
		  );
		  return dlmmPool.removeLiquidity({
			position: publicKey,
			user: user.publicKey,
			binIds: binIdsToRemove,
			bps: new BN(100 * 100),
			shouldClaimAndClose: true, // should claim swap fee and close position together
		  });
		})
	  )
	).flat();
  
	try {
	  for (let tx of removeLiquidityTxs) {
		const removeBalanceLiquidityTxHash = await sendAndConfirmTransaction(
		  connection,
		  tx,
		  [user],
		  { skipPreflight: false, preflightCommitment: "confirmed" }
		);
		console.log(
		  "🚀 ~ removeBalanceLiquidityTxHash:",
		  removeBalanceLiquidityTxHash
		);
	  }
	} catch (error) {
	  console.log("🚀 ~ error:", JSON.parse(JSON.stringify(error)));
	}
  }
  
  
export async function swap(dlmmPool: DLMM) {
	const swapAmount = new BN(100);
	// Swap quote
	const swapYtoX = true;
	const binArrays = await dlmmPool.getBinArrayForSwap(swapYtoX);
  
	const swapQuote = await dlmmPool.swapQuote(swapAmount, swapYtoX, new BN(10), binArrays);
  
	console.log("🚀 ~ swapQuote:", swapQuote);
  
	// Swap
	const swapTx = await dlmmPool.swap({
	  inToken: dlmmPool.tokenX.publicKey,
	  binArraysPubkey: swapQuote.binArraysPubkey,
	  inAmount: swapAmount,
	  lbPair: dlmmPool.pubkey,
	  user: user.publicKey,
	  minOutAmount: swapQuote.minOutAmount,
	  outToken: dlmmPool.tokenY.publicKey,
	});
  
	try {
	  const swapTxHash = await sendAndConfirmTransaction(connection, swapTx, [
		user,
	  ]);
	  console.log("🚀 ~ swapTxHash:", swapTxHash);
	} catch (error) {
	  console.log("🚀 ~ error:", JSON.parse(JSON.stringify(error)));
	}
  }


  async function getImpermanentLoss(dlmmPool: DLMM): Promise<number> {
	// Get user's positions
	const userPositions = await dlmmPool.getPositionsByUserAndLbPair(user.publicKey);
  
	if (!userPositions || userPositions.userPositions.length === 0) {
	  console.log("No user positions found.");
	  return 0;
	}
  
	// Loop through all positions and calculate IL for each
	let totalIL = 0;
  
	for (const position of userPositions.userPositions) {
	  const positionData = position.positionData;
  
	  // Get current price of the active bin
	  const activeBin = await dlmmPool.getActiveBin();
	  const currentPrice = Number(dlmmPool.fromPricePerLamport(Number(activeBin.price)));
  
	  // Get initial price when liquidity was added
	  const initialTokenXAmount = positionData.positionBinData.reduce(
		(acc, bin) => acc.add(new BN(bin.binXAmount)),
		new BN(0)
	  );
  
	  const initialTokenYAmount = positionData.positionBinData.reduce(
		(acc, bin) => acc.add(new BN(bin.binYAmount)),
		new BN(0)
	  );
  
	  const initialPrice = initialTokenYAmount.toNumber() / initialTokenXAmount.toNumber();
  
	  // Calculate ratio
	  const priceRatio = currentPrice / initialPrice;
  
	  // Calculate IL using the formula
	  const il = 1 - Math.sqrt(2 / (1 + priceRatio)) * priceRatio;
	  totalIL += il;
  
	  console.log(`Position ${position.publicKey.toBase58()} - IL: ${il}`);
	}
  
	return totalIL / userPositions.userPositions.length; 
  }
  


  async function checkStopLoss(dlmmPool: DLMM) {
	// Fetch user positions
	const userPositions = await dlmmPool.getPositionsByUserAndLbPair(user.publicKey);
  
	if (!userPositions || userPositions.userPositions.length === 0) {
	  console.log("No user positions found.");
	  return;
	}
  
	for (const position of userPositions.userPositions) {
	  const positionData = position.positionData;
  
	  // Calculate initial price from position bin data
	  const initialTokenXAmount = positionData.positionBinData.reduce(
		(acc, bin) => acc.add(new BN(bin.binXAmount)),
		new BN(0)
	  );
  
	  const initialTokenYAmount = positionData.positionBinData.reduce(
		(acc, bin) => acc.add(new BN(bin.binYAmount)),
		new BN(0)
	  );
  
	  if (initialTokenXAmount.isZero() || initialTokenYAmount.isZero()) {
		console.log("Invalid bin data for position:", position.publicKey.toBase58());
		continue;
	  }
  
	  const initialPrice = initialTokenYAmount.toNumber() / initialTokenXAmount.toNumber();
  
	  // Get current price of the active bin
	  const activeBin = await dlmmPool.getActiveBin();
	  const currentPrice = Number(dlmmPool.fromPricePerLamport(Number(activeBin.price)));
  
	  // Calculate stop-loss condition
	  const priceDrop = (initialPrice - currentPrice) / initialPrice;
  
	  return priceDrop;
	}
  }

  async function getTradeVolumeChange(pairAddress: string, numOfDays: number): Promise<number> {
	const API_BASE_URL = "https://your-api-base-url.com"; // Replace with your API base URL
	const endpoint = `/pair/${pairAddress}/analytic/pair_trade_volume`;
  
	try {
	  // Fetch trade volume data from the API
	  const response = await axios.get(`${API_BASE_URL}${endpoint}`, {
		params: { num_of_days: numOfDays },
	  });
  
	  const data = response.data;
  
	  if (!data || data.length < 2) {
		throw new Error("Insufficient data for calculating trade volume change.");
	  }
  
	  // Extract the two most recent trade volumes
	  const currentVolume = data[data.length - 1].trade_volume; // Most recent day
	  const previousVolume = data[data.length - 2].trade_volume; // One day prior
  
	  if (previousVolume === 0) {
		throw new Error("Previous volume is zero, cannot calculate change.");
	  }
  
	  // Calculate percentage change in trade volume
	  const volumeChange = ((currentVolume - previousVolume) / previousVolume) * 100;
  
	  console.log(`Trade Volume Change: ${volumeChange.toFixed(2)}%`);
	  return volumeChange;
	} catch (error) {
	  console.error("Error fetching or processing trade volume data:", (error as Error).message);
	  throw error;
	}
  }
  
  

export  async function manageRisk(dlmmPool: DLMM) {
	/*
		health score is above 70
		IL is below 0.015
		STOP LOSS is below 0.05
		VOLUME CHANGE is below 0.4
	*/

	// health score 

	// IL

	if(await getImpermanentLoss(dlmmPool) > RISK_PARAMS.MAX_IL) {
		removePositionLiquidity(dlmmPool);
	}

	// STOP LOSS
	const stopLoss = await checkStopLoss(dlmmPool);
	if(stopLoss) {
		if(stopLoss > RISK_PARAMS.STOP_LOSS) {
			removePositionLiquidity(dlmmPool);
		}
	}
	
	// VOLUME CHANGE
	const volumeChange = await getTradeVolumeChange(dlmmPool.pubkey.toBase58(), 1);
	if(volumeChange > RISK_PARAMS.VOLUME_DROP_THRESHOLD) {
		removePositionLiquidity(dlmmPool);
	}
  }