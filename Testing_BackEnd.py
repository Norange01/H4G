import BackEnd as backend
import time

msg = "Patient with suspected adrenal tumor, age 40, female."
condensed = backend.message_condenser(msg)
time.sleep (2)
unpacked = backend.unpack_message(condensed)
time.sleep (2)
matched_doctors = backend.doctor_matching(unpacked)
time.sleep (2)
# You can then show the case in the "new cases" tab for the matched doctors

