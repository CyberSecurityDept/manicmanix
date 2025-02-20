output=$(bash app/utils/bash/imei.sh 2>/dev/null | grep -E "^IMEI: [0-9]+" | sort | uniq)

imei1=$(echo "$output" | sed -n '1s/IMEI: //p')
imei2=$(echo "$output" | sed -n '2s/IMEI: //p')

echo "IMEI 1: $imei1"
echo "IMEI 2: $imei2"
