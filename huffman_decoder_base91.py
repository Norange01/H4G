
import base91

def load_huffman_codes(file_path):
    with open(file_path, 'r') as f:
        return dict(line.strip().split(':', 1) for line in f if ':' in line)

def invert_dict(d):
    return {v: k for k, v in d.items()}

word_codes = load_huffman_codes("word_huffman_codes.txt")
char_codes = load_huffman_codes("char_huffman_codes.txt")
inv_word_codes = invert_dict(word_codes)
inv_char_codes = invert_dict(char_codes)

def decode_message(full_encoded):
    padding = int(full_encoded[-1])
    b64_encoded = full_encoded[:-1]
    bitstream = bin(int.from_bytes(base91.decode(b64_encoded), 'big'))[2:]
    bitstream = bitstream.zfill(len(bitstream) + (8 - len(bitstream) % 8) % 8)
    bitstream = bitstream[:-padding] if padding else bitstream

    i = 0
    decoded_tokens = []
    while i < len(bitstream):
        prefix = bitstream[i]
        i += 1
        if prefix == '0':
            for j in range(i + 1, len(bitstream) + 1):
                segment = bitstream[i:j]
                if segment in inv_word_codes:
                    decoded_tokens.append(inv_word_codes[segment])
                    i = j
                    break
        elif prefix == '1':
            char_count = int(bitstream[i:i+5], 2)
            i += 5
            chars = []
            while len(chars) < char_count:
                for j in range(i + 1, len(bitstream) + 1):
                    segment = bitstream[i:j]
                    if segment in inv_char_codes:
                        chars.append(inv_char_codes[segment])
                        i = j
                        break
            decoded_tokens.append(''.join(chars))
    return ' '.join(decoded_tokens)

if __name__ == "__main__":
    full_encoded = input("Enter encoded message with padding digit at end: ")
    print("Decoded:", decode_message(full_encoded))
