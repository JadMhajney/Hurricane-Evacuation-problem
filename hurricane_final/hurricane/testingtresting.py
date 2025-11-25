def shuffle_playlist(playlist):
    from collections import defaultdict
    import heapq
    
    # Group songs by artist with original indices
    artist_songs = defaultdict(list)
    for idx, (title, artist) in enumerate(playlist):
        artist_songs[artist].append((idx, title))
    
    # Max heap: (-remaining_songs, first_song_original_idx, artist, current_pos)
    # Negative remaining_songs for max heap behavior
    heap = []
    for artist, songs in artist_songs.items():
        heapq.heappush(heap, (-len(songs), songs[0][0], artist, 0))
    
    result = []
    last_artist = None
    temp_storage = None  # Temporarily hold artist if same as last
    
    while heap or temp_storage:
        # If heap is empty but we have stored artist, it must be the last one
        if not heap and temp_storage:
            heap = [temp_storage]
            temp_storage = None
        
        # Pop highest priority artist
        neg_remaining, first_idx, artist, pos = heapq.heappop(heap)
        
        # If same as last artist and we have other options
        if artist == last_artist and heap:
            # Store this artist temporarily
            temp_storage = (neg_remaining, first_idx, artist, pos)
            continue
        
        # If we had a stored artist and current is different, push stored back
        if temp_storage and temp_storage[2] != artist:
            heapq.heappush(heap, temp_storage)
            temp_storage = None
        
        # Play the song
        original_idx, title = artist_songs[artist][pos]
        result.append([title, artist])
        last_artist = artist
        
        # Update: move to next song for this artist
        pos += 1
        remaining = len(artist_songs[artist]) - pos
        
        # If artist has more songs, push back to heap
        if remaining > 0:
            next_first_idx = artist_songs[artist][pos][0]
            heapq.heappush(heap, (-remaining, next_first_idx, artist, pos))
    
    return result


# COMPREHENSIVE TEST SUITE
def run_all_tests():
    print("=" * 80)
    print("TESTING OPTIMIZED O(n log m) SOLUTION")
    print("=" * 80)
    
    # Test 1: Original Example
    print("\nTEST 1: Original Example")
    playlist1 = [
        ["Photograph", "EdSheeran"],
        ["Perfect", "EdSheeran"],
        ["BlindingLights", "TheWeeknd"],
        ["Shivers", "EdSheeran"],
        ["Tides", "EdSheeran"],
        ["BlankSpace", "TaylorSwift"],
        ["BlankSpace", "TaylorSwift"]  
    ]
    result1 = shuffle_playlist(playlist1)
    expected1 = [
        ["Photograph", "EdSheeran"],
        ["BlindingLights", "TheWeeknd"],
        ["Perfect", "EdSheeran"],
        ["BlankSpace", "TaylorSwift"],
        ["Shivers", "EdSheeran"],
        ["BlankSpace", "TaylorSwift"],
        ["Tides", "EdSheeran"]
    ]
    print("✓ PASS" if result1 == expected1 else "✗ FAIL")
    if result1 != expected1:
        print("Expected:", expected1)
        print("Got:", result1)
    
    # Test 2: Single Artist
    print("\nTEST 2: Single Artist")
    playlist2 = [["S1", "A1"], ["S2", "A1"], ["S3", "A1"]]
    result2 = shuffle_playlist(playlist2)
    expected2 = [["S1", "A1"], ["S2", "A1"], ["S3", "A1"]]
    print("✓ PASS" if result2 == expected2 else "✗ FAIL")
    
    # Test 3: All Different Artists
    print("\nTEST 3: All Different Artists")
    playlist3 = [["S1", "A1"], ["S2", "A2"], ["S3", "A3"]]
    result3 = shuffle_playlist(playlist3)
    expected3 = [["S1", "A1"], ["S2", "A2"], ["S3", "A3"]]
    print("✓ PASS" if result3 == expected3 else "✗ FAIL")
    
    # Test 4: Two Artists Equal Songs
    print("\nTEST 4: Two Artists Equal Songs")
    playlist4 = [["S1", "A1"], ["S2", "A2"], ["S3", "A1"], ["S4", "A2"]]
    result4 = shuffle_playlist(playlist4)
    expected4 = [["S1", "A1"], ["S2", "A2"], ["S3", "A1"], ["S4", "A2"]]
    print("✓ PASS" if result4 == expected4 else "✗ FAIL")
    
    # Test 5: One Artist Dominates
    print("\nTEST 5: One Artist Dominates")
    playlist5 = [["A1", "X"], ["A2", "X"], ["A3", "X"], ["A4", "X"], ["B1", "Y"]]
    result5 = shuffle_playlist(playlist5)
    expected5 = [["A1", "X"], ["B1", "Y"], ["A2", "X"], ["A3", "X"], ["A4", "X"]]
    print("✓ PASS" if result5 == expected5 else "✗ FAIL")
    
    # Test 6: Tie-Breaking by Position
    print("\nTEST 6: Tie-Breaking by Position")
    playlist6 = [
        ["X1", "X"], ["Y1", "Y"], ["Z1", "Z"],
        ["X2", "X"], ["Y2", "Y"], ["Z2", "Z"]
    ]
    result6 = shuffle_playlist(playlist6)
    expected6 = [
        ["X1", "X"], ["Y1", "Y"], ["Z1", "Z"],
        ["X2", "X"], ["Y2", "Y"], ["Z2", "Z"]
    ]
    print("✓ PASS" if result6 == expected6 else "✗ FAIL")
    
    # Test 7: Complex Scenario
    print("\nTEST 7: Complex Scenario")
    playlist7 = [
        ["C1", "C"], ["A1", "A"], ["B1", "B"],
        ["A2", "A"], ["C2", "C"], ["A3", "A"]
    ]
    result7 = shuffle_playlist(playlist7)
    # A has 3 songs (most), first at idx 1
    # After A1, C and B both have 2 and 1 songs
    # C has 2 remaining, first at idx 0
    expected7 = [["A1", "A"], ["C1", "C"], ["A2", "A"], ["B1", "B"], ["A3", "A"], ["C2", "C"]]
    print("✓ PASS" if result7 == expected7 else "✗ FAIL")
    if result7 != expected7:
        print("Expected:", expected7)
        print("Got:", result7)
    
    # Test 8: Forced Consecutive
    print("\nTEST 8: Forced Consecutive")
    playlist8 = [["X1", "X"], ["Y1", "Y"], ["Y2", "Y"], ["Y3", "Y"]]
    result8 = shuffle_playlist(playlist8)
    expected8 = [["Y1", "Y"], ["X1", "X"], ["Y2", "Y"], ["Y3", "Y"]]
    print("✓ PASS" if result8 == expected8 else "✗ FAIL")
    
    # Test 9: All Songs from One Artist at Start
    print("\nTEST 9: All Songs from One Artist at Start")
    playlist9 = [["A1", "A"], ["A2", "A"], ["A3", "A"], ["B1", "B"], ["C1", "C"]]
    result9 = shuffle_playlist(playlist9)
    expected9 = [["A1", "A"], ["B1", "B"], ["A2", "A"], ["C1", "C"], ["A3", "A"]]
    print("✓ PASS" if result9 == expected9 else "✗ FAIL")
    
    # Test 10: Alternating Pattern
    print("\nTEST 10: Alternating Pattern")
    playlist10 = [["A1", "A"], ["B1", "B"], ["A2", "A"], ["B2", "B"], ["A3", "A"]]
    result10 = shuffle_playlist(playlist10)
    expected10 = [["A1", "A"], ["B1", "B"], ["A2", "A"], ["B2", "B"], ["A3", "A"]]
    print("✓ PASS" if result10 == expected10 else "✗ FAIL")
    
    # Test 11: Single Song
    print("\nTEST 11: Single Song")
    playlist11 = [["Only", "Artist"]]
    result11 = shuffle_playlist(playlist11)
    expected11 = [["Only", "Artist"]]
    print("✓ PASS" if result11 == expected11 else "✗ FAIL")
    
    # Test 12: Two Songs
    print("\nTEST 12: Two Songs")
    playlist12 = [["S1", "A1"], ["S2", "A2"]]
    result12 = shuffle_playlist(playlist12)
    expected12 = [["S1", "A1"], ["S2", "A2"]]
    print("✓ PASS" if result12 == expected12 else "✗ FAIL")
    
    # Test 13: Stress Test - Heavy Dominant
    print("\nTEST 13: Stress Test")
    playlist13 = [
        ["D1", "D"], ["D2", "D"], ["D3", "D"], ["D4", "D"],
        ["D5", "D"], ["D6", "D"], ["D7", "D"],
        ["O1", "X"], ["O2", "Y"]
    ]
    result13 = shuffle_playlist(playlist13)
    expected13 = [
        ["D1", "D"], ["O1", "X"], ["D2", "D"], ["O2", "Y"],
        ["D3", "D"], ["D4", "D"], ["D5", "D"], ["D6", "D"], ["D7", "D"]
    ]
    print("✓ PASS" if result13 == expected13 else "✗ FAIL")
    
    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETED!")
    print("=" * 80)

run_all_tests()