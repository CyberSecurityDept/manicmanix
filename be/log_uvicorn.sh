#!/bin/bash

LOG_PATH="/home/manic/malware-analysis/manicmanix/be/logs/uvicorn.out.log"

if [[ ! -f "$LOG_PATH" ]]; then
    echo -e "\e[31m[ERROR]\e[0m File log tidak ditemukan di path: $LOG_PATH"
    exit 1
fi

echo -e "\e[32m[INFO]\e[0m Memantau file log uvicorn secara real-time:"
echo -e "  \e[33mPath Log:\e[0m $LOG_PATH\n"
echo -e "\e[36m[KONTEN LOG]\e[0m Tekan CTRL+C untuk keluar.\n"

tail -f "$LOG_PATH" | while IFS= read -r LINE; do
    if [[ "$LINE" == *"ERROR"* || "$LINE" == *"error"* ]]; then
        echo -e "\e[31m$LINE\e[0m"  # Warna merah untuk error
    elif [[ "$LINE" == *"INFO"* || "$LINE" == *"info"* ]]; then
        echo -e "\e[32m$LINE\e[0m"  # Warna hijau untuk info
    elif [[ "$LINE" == *"WARNING"* || "$LINE" == *"warning"* ]]; then
        echo -e "\e[33m$LINE\e[0m"  # Warna kuning untuk warning
    else
        echo "$LINE"                # Baris lain tanpa warna tambahan
    fi
done

echo -e "\n\e[32m[SELESAI]\e[0m Pemantauan log dihentikan."
