
import ftplib
import os

service_login = os.environ['SERVICE_LOGIN']
service_password = os.environ['SERVICE_PASSWORD']

def getFile(ftp, filename):
    try:
        ftp.retrbinary("RETR " + filename ,open(filename, 'wb').write)
    except:
        print("Error")

def get_file_from_ftp():

    ftp = ftplib.FTP("ftp.eoddata.com")
    ftp.login(service_login, service_password)
    data = []
    ftp.dir(data.append)
    getFile(ftp, "NYSE_20210607.txt")

    ftp.quit()
    for line in data:
        print("- ", line)

if __name__ == '__main__':
   get_file_from_ftp()



