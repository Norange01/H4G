import pandas as pd

def message_condenser(message):
    print(f"[Condenser] Received message: {message}")
    condensed = f"{message[:30]}..."
    print(f"[Condenser] Condensed message: {condensed}")
    return condensed

def unpack_message(condensed_message):
    print(f"[Unpacker] Unpacking")
    unpacked = condensed_message
    print(f"[Unpacker] Unpacked message: {unpacked}")
    return unpacked

def load_doctor_data(csv_path='fake_doctors.csv'):
    df = pd.read_csv(csv_path)
    return df

def doctor_matching(unpacked_message, csv_path='Fake_Doctors_Dataset.csv'):
    df = load_doctor_data(csv_path)
    print ("")
    online_doctors = df[df["Online"] == True].head(5)  # Limit to first 5

    print(f"[Matcher] Finding Best Docotors To Help With: {unpacked_message}")
    print(f"[Matcher] Found {len(online_doctors)} online doctors.")

    # For now, return all online doctors
    matched = online_doctors.to_dict(orient='records')
    print(f"[Matcher] Matched doctors: {[doc['first_name'] for doc in matched]}")
    return matched
