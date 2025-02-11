export function mapToJson(map: Map<string, any>): Record<string, any> {
    const jsonObject: Record<string, any> = {};

    map.forEach((value, key) => {
        jsonObject[key] = {
            publicKey: value.publicKey.toBase58(),
            lbPair: {
                pairType: value.lbPair.pairType,
                activeId: value.lbPair.activeId,
                binStep: value.lbPair.binStep,
                status: value.lbPair.status,
                tokenXMint: value.lbPair.tokenXMint.toBase58(),
                tokenYMint: value.lbPair.tokenYMint.toBase58(),
                reserveX: value.lbPair.reserveX.toBase58(),
                reserveY: value.lbPair.reserveY.toBase58(),
                oracle: value.lbPair.oracle.toBase58(),
                creator: value.lbPair.creator.toBase58(),
            },
            tokenX: {
                publicKey: value.tokenX.publicKey.toBase58(),
                reserve: value.tokenX.reserve.toBase58(),
                amount: value.tokenX.amount.toString(),
                decimal: value.tokenX.decimal,
            },
            tokenY: {
                publicKey: value.tokenY.publicKey.toBase58(),
                reserve: value.tokenY.reserve.toBase58(),
                amount: value.tokenY.amount.toString(),
                decimal: value.tokenY.decimal,
            },
            lbPairPositionsData: value.lbPairPositionsData
        };
    });

    return jsonObject;
}
