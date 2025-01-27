from investable_pairs import InvestablePairs

if __name__ == "__main__":
    pairs = InvestablePairs()
    num_pairs = pairs.update()
    print(f"Updated {num_pairs} investable pairs")