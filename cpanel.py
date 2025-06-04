from cpanel_api import CPanelApi
from utils import read_file, write_file
import time

hostname = 'ip' #sunucunun ip adresi (tırnak işaretlerinin arasına girilecek)
username = 'user' #host kullanıcı adı (tırnak işaretlerinin arasına girilecek)
password = 'sifre' #host şifresi (tırnak işaretlerinin arasına girilecek)

# cPANEL - timeout'u artırarak bağlantı süresini yükselttik
client = CPanelApi(hostname, username, password, timeout=20)

# Domains
domains = read_file("cpanel_domains.txt")
domains = domains.split("\n")

failed_domains = []

for domain in domains:
    domain = domain.strip()
    if domain:
        retry_attempts = 3  # Yeniden deneme sayısı
        for attempt in range(retry_attempts):
            try:
                r = client.cpanel2.Park.park({"domain": domain})
                if r.cpanelresult.data[0].result == 1:
                    print(f"Domain({domain}) added successfully to Park")
                    break  # Başarılı olduysa döngüden çık
                else:
                    error_message = r.cpanelresult.data[0].reason
                    if "already exists" in error_message:
                        print(f"Domain({domain}) already exists, skipping.")
                        break  # Domain zaten mevcutsa geç
                    else:
                        print(f"Domain({domain}) failed to add Park: {error_message}")
                        failed_domains.append(domain)
                        break
            except Exception as e:
                print(f"Error with domain {domain}: {str(e)} - Attempt {attempt + 1} of {retry_attempts}")
                time.sleep(5)  # Hata durumunda 5 saniye bekleyip tekrar dene
                if attempt == retry_attempts - 1:  # Tüm denemeler başarısız olursa domaini başarısız listesine ekle
                    failed_domains.append(domain)

# Başarısız domainleri failed_domains.txt dosyasına yazdır
if failed_domains:
    write_file("failed_domains.txt", "\n".join(failed_domains))
