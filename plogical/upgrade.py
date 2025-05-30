import json
import os
import os.path
import sys
import argparse
import pwd
import grp

sys.path.append('/usr/local/CyberCP')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CyberCP.settings")
import shlex
import subprocess
import shutil
import time
import MySQLdb as mysql
from CyberCP import settings
import random
import string

VERSION = '2.4'
BUILD = 0

CENTOS7 = 0
CENTOS8 = 1
Ubuntu18 = 2
Ubuntu20 = 3
CloudLinux7 = 4
CloudLinux8 = 5
openEuler20 = 6
openEuler22 = 7
Ubuntu22 = 8


class Upgrade:
    logPath = "/usr/local/lscp/logs/upgradeLog"
    cdn = 'cdn.cyberpanel.sh'
    installedOutput = ''
    CentOSPath = '/etc/redhat-release'
    UbuntuPath = '/etc/lsb-release'
    openEulerPath = '/etc/openEuler-release'
    FromCloud = 0
    SnappyVersion = '2.38.2'
    LogPathNew = '/home/cyberpanel/upgrade_logs'
    SoftUpgrade = 0

    AdminACL = '{"adminStatus":1, "versionManagement": 1, "createNewUser": 1, "listUsers": 1, "deleteUser":1 , "resellerCenter": 1, ' \
               '"changeUserACL": 1, "createWebsite": 1, "modifyWebsite": 1, "suspendWebsite": 1, "deleteWebsite": 1, ' \
               '"createPackage": 1, "listPackages": 1, "deletePackage": 1, "modifyPackage": 1, "createDatabase": 1, "deleteDatabase": 1, ' \
               '"listDatabases": 1, "createNameServer": 1, "createDNSZone": 1, "deleteZone": 1, "addDeleteRecords": 1, ' \
               '"createEmail": 1, "listEmails": 1, "deleteEmail": 1, "emailForwarding": 1, "changeEmailPassword": 1, ' \
               '"dkimManager": 1, "createFTPAccount": 1, "deleteFTPAccount": 1, "listFTPAccounts": 1, "createBackup": 1,' \
               ' "restoreBackup": 1, "addDeleteDestinations": 1, "scheduleBackups": 1, "remoteBackups": 1, "googleDriveBackups": 1, "manageSSL": 1, ' \
               '"hostnameSSL": 1, "mailServerSSL": 1 }'

    ResellerACL = '{"adminStatus":0, "versionManagement": 1, "createNewUser": 1, "listUsers": 1, "deleteUser": 1 , "resellerCenter": 1, ' \
                  '"changeUserACL": 0, "createWebsite": 1, "modifyWebsite": 1, "suspendWebsite": 1, "deleteWebsite": 1, ' \
                  '"createPackage": 1, "listPackages": 1, "deletePackage": 1, "modifyPackage": 1, "createDatabase": 1, "deleteDatabase": 1, ' \
                  '"listDatabases": 1, "createNameServer": 1, "createDNSZone": 1, "deleteZone": 1, "addDeleteRecords": 1, ' \
                  '"createEmail": 1, "listEmails": 1, "deleteEmail": 1, "emailForwarding": 1, "changeEmailPassword": 1, ' \
                  '"dkimManager": 1, "createFTPAccount": 1, "deleteFTPAccount": 1, "listFTPAccounts": 1, "createBackup": 1,' \
                  ' "restoreBackup": 1, "addDeleteDestinations": 0, "scheduleBackups": 0, "remoteBackups": 0, "googleDriveBackups": 1, "manageSSL": 1, ' \
                  '"hostnameSSL": 0, "mailServerSSL": 0 }'

    UserACL = '{"adminStatus":0, "versionManagement": 1, "createNewUser": 0, "listUsers": 0, "deleteUser": 0 , "resellerCenter": 0, ' \
              '"changeUserACL": 0, "createWebsite": 0, "modifyWebsite": 0, "suspendWebsite": 0, "deleteWebsite": 0, ' \
              '"createPackage": 0, "listPackages": 0, "deletePackage": 0, "modifyPackage": 0, "createDatabase": 1, "deleteDatabase": 1, ' \
              '"listDatabases": 1, "createNameServer": 0, "createDNSZone": 1, "deleteZone": 1, "addDeleteRecords": 1, ' \
              '"createEmail": 1, "listEmails": 1, "deleteEmail": 1, "emailForwarding": 1, "changeEmailPassword": 1, ' \
              '"dkimManager": 1, "createFTPAccount": 1, "deleteFTPAccount": 1, "listFTPAccounts": 1, "createBackup": 1,' \
              ' "restoreBackup": 0, "addDeleteDestinations": 0, "scheduleBackups": 0, "remoteBackups": 0, "googleDriveBackups": 1, "manageSSL": 1, ' \
              '"hostnameSSL": 0, "mailServerSSL": 0 }'

    @staticmethod
    def FetchCloudLinuxAlmaVersionVersion():
        if os.path.exists('/etc/os-release'):
            data = open('/etc/os-release', 'r').read()
            if (data.find('CloudLinux') > -1 or data.find('cloudlinux') > -1) and (
                    data.find('8.9') > -1 or data.find('Anatoly Levchenko') > -1 or data.find('VERSION="8.') > -1):
                return 'cl-89'
            elif (data.find('CloudLinux') > -1 or data.find('cloudlinux') > -1) and (
                    data.find('8.8') > -1 or data.find('Anatoly Filipchenko') > -1):
                return 'cl-88'
            elif (data.find('CloudLinux') > -1 or data.find('cloudlinux') > -1) and (
                    data.find('9.4') > -1 or data.find('VERSION="9.') > -1):
                return 'cl-88'
            elif (data.find('AlmaLinux') > -1 or data.find('almalinux') > -1) and (
                    data.find('8.9') > -1 or data.find('Midnight Oncilla') > -1 or data.find('VERSION="8.') > -1):
                return 'al-88'
            elif (data.find('AlmaLinux') > -1 or data.find('almalinux') > -1) and (
                    data.find('8.7') > -1 or data.find('Stone Smilodon') > -1):
                return 'al-87'
            elif (data.find('AlmaLinux') > -1 or data.find('almalinux') > -1) and (
                    data.find('9.4') > -1 or data.find('9.3') > -1 or data.find('Shamrock Pampas') > -1 or data.find(
                    'Seafoam Ocelot') > -1 or data.find('VERSION="9.') > -1):
                return 'al-93'
        else:
            return -1

    @staticmethod
    def decideCentosVersion():

        if open(Upgrade.CentOSPath, 'r').read().find('CentOS Linux release 8') > -1:
            return CENTOS8
        else:
            return CENTOS7

    @staticmethod
    def FindOperatingSytem():

        if os.path.exists(Upgrade.CentOSPath):
            result = open(Upgrade.CentOSPath, 'r').read()

            if result.find('CentOS Linux release 8') > -1 or result.find('CloudLinux release 8') > -1:
                return CENTOS8
            else:
                return CENTOS7

        elif os.path.exists(Upgrade.openEulerPath):
            result = open(Upgrade.openEulerPath, 'r').read()

            if result.find('20.03') > -1:
                return openEuler20
            elif result.find('22.03') > -1:
                return openEuler22

        else:
            result = open(Upgrade.UbuntuPath, 'r').read()

            if result.find('20.04') > -1:
                return Ubuntu20
            elif result.find('22.04') > -1:
                return Ubuntu22
            else:
                return Ubuntu18

    @staticmethod
    def stdOut(message, do_exit=0):
        print("\n\n")
        print(("[" + time.strftime(
            "%m.%d.%Y_%H-%M-%S") + "] #########################################################################\n"))
        print(("[" + time.strftime("%m.%d.%Y_%H-%M-%S") + "] " + message + "\n"))
        print(("[" + time.strftime(
            "%m.%d.%Y_%H-%M-%S") + "] #########################################################################\n"))

        WriteToFile = open(Upgrade.LogPathNew, 'a')
        WriteToFile.write(("[" + time.strftime(
            "%m.%d.%Y_%H-%M-%S") + "] #########################################################################\n"))
        WriteToFile.write(("[" + time.strftime("%m.%d.%Y_%H-%M-%S") + "] " + message + "\n"))
        WriteToFile.write(("[" + time.strftime(
            "%m.%d.%Y_%H-%M-%S") + "] #########################################################################\n"))
        WriteToFile.close()

        if do_exit:

            ### remove log file path incase its there

            if Upgrade.SoftUpgrade:
                time.sleep(10)
                if os.path.exists(Upgrade.LogPathNew):
                    os.remove(Upgrade.LogPathNew)

            if Upgrade.FromCloud == 0:
                os._exit(0)

    @staticmethod
    def executioner(command, component, do_exit=0, shell=False):
        try:
            FNULL = open(os.devnull, 'w')
            count = 0
            while True:
                if shell == False:
                    res = subprocess.call(shlex.split(command), stderr=subprocess.STDOUT)
                else:
                    res = subprocess.call(command, stderr=subprocess.STDOUT, shell=True)
                if res != 0:
                    count = count + 1
                    Upgrade.stdOut(component + ' failed, trying again, try number: ' + str(count), 0)
                    if count == 3:
                        Upgrade.stdOut(component + ' failed.', do_exit)
                        return False
                else:
                    Upgrade.stdOut(component + ' successful.', 0)
                    break
            return True
        except:
            return False

    @staticmethod
    def updateRepoURL():
        command = "sed -i 's|sgp.cyberpanel.sh|cdn.cyberpanel.sh|g' /etc/yum.repos.d/MariaDB.repo"
        Upgrade.executioner(command, command, 0)

        command = "sed -i 's|lax.cyberpanel.sh|cdn.cyberpanel.sh|g' /etc/yum.repos.d/MariaDB.repo"
        Upgrade.executioner(command, command, 0)

        command = "sed -i 's|fra.cyberpanel.sh|cdn.cyberpanel.sh|g' /etc/yum.repos.d/MariaDB.repo"
        Upgrade.executioner(command, command, 0)

        command = "sed -i 's|mirror.cyberpanel.net|cdn.cyberpanel.sh|g' /etc/yum.repos.d/MariaDB.repo"
        Upgrade.executioner(command, command, 0)

        command = "sed -i 's|sgp.cyberpanel.sh|cdn.cyberpanel.sh|g' /etc/yum.repos.d/litespeed.repo"
        Upgrade.executioner(command, command, 0)

        command = "sed -i 's|lax.cyberpanel.sh|cdn.cyberpanel.sh|g' /etc/yum.repos.d/litespeed.repo"
        Upgrade.executioner(command, command, 0)

        command = "sed -i 's|fra.cyberpanel.sh|cdn.cyberpanel.sh|g' /etc/yum.repos.d/litespeed.repo"
        Upgrade.executioner(command, command, 0)

        command = "sed -i 's|mirror.cyberpanel.net|cdn.cyberpanel.sh|g' /etc/yum.repos.d/litespeed.repo"
        Upgrade.executioner(command, command, 0)

    @staticmethod
    def mountTemp():
        try:

            if os.path.exists("/usr/.tempdisk"):
                return 0

            command = "dd if=/dev/zero of=/usr/.tempdisk bs=100M count=15"
            Upgrade.executioner(command, 'mountTemp', 0)

            command = "mkfs.ext4 -F /usr/.tempdisk"
            Upgrade.executioner(command, 'mountTemp', 0)

            command = "mkdir -p /usr/.tmpbak/"
            Upgrade.executioner(command, 'mountTemp', 0)

            command = "cp -pr /tmp/* /usr/.tmpbak/"
            subprocess.call(command, shell=True)

            command = "mount -o loop,rw,nodev,nosuid,noexec,nofail /usr/.tempdisk /tmp"
            Upgrade.executioner(command, 'mountTemp', 0)

            command = "chmod 1777 /tmp"
            Upgrade.executioner(command, 'mountTemp', 0)

            command = "cp -pr /usr/.tmpbak/* /tmp/"
            subprocess.call(command, shell=True)

            command = "rm -rf /usr/.tmpbak"
            Upgrade.executioner(command, 'mountTemp', 0)

            command = "mount --bind /tmp /var/tmp"
            Upgrade.executioner(command, 'mountTemp', 0)

            tmp = "/usr/.tempdisk /tmp ext4 loop,rw,noexec,nosuid,nodev,nofail 0 0\n"
            varTmp = "/tmp /var/tmp none bind 0 0\n"

            fstab = "/etc/fstab"
            writeToFile = open(fstab, "a")
            writeToFile.writelines(tmp)
            writeToFile.writelines(varTmp)
            writeToFile.close()

        except BaseException as msg:
            Upgrade.stdOut(str(msg) + " [mountTemp]", 0)

    @staticmethod
    def dockerUsers():
        ### Docker User/group
        try:
            pwd.getpwnam('docker')
        except KeyError:
            command = "adduser docker"
            Upgrade.executioner(command, 'adduser docker', 0)

        try:
            grp.getgrnam('docker')
        except KeyError:
            command = 'groupadd docker'
            Upgrade.executioner(command, 'adduser docker', 0)

        command = 'usermod -aG docker docker'
        Upgrade.executioner(command, 'adduser docker', 0)

        command = 'usermod -aG docker cyberpanel'
        Upgrade.executioner(command, 'adduser docker', 0)

        ###

    @staticmethod
    def fixSudoers():
        try:
            distroPath = '/etc/lsb-release'

            if os.path.exists(distroPath):
                fileName = '/etc/sudoers'
                data = open(fileName, 'r').readlines()

                writeDataToFile = open(fileName, 'w')
                for line in data:
                    if line.find("%sudo ALL=(ALL:ALL)") > -1:
                        continue
                    else:
                        writeDataToFile.write(line)
                writeDataToFile.close()

            else:
                try:
                    path = "/etc/sudoers"

                    data = open(path, 'r').readlines()

                    writeToFile = open(path, 'w')

                    for items in data:
                        if items.find("wheel") > -1 and items.find("ALL=(ALL)"):
                            continue
                        elif items.find("root") > -1 and items.find("ALL=(ALL)") > -1 and items[0] != '#':
                            writeToFile.writelines('root	ALL=(ALL:ALL) 	ALL\n')
                        else:
                            writeToFile.writelines(items)

                    writeToFile.close()
                except:
                    pass

            command = "chsh -s /bin/false cyberpanel"
            Upgrade.executioner(command, 0)
        except IOError as err:
            pass

    @staticmethod
    def download_install_phpmyadmin():
        try:
            cwd = os.getcwd()

            if not os.path.exists("/usr/local/CyberCP/public"):
                os.mkdir("/usr/local/CyberCP/public")

            try:
                shutil.rmtree("/usr/local/CyberCP/public/phpmyadmin")
            except:
                pass

            command = 'wget -O /usr/local/CyberCP/public/phpmyadmin.zip https://github.com/quantum-host/webpanel/raw/stable/phpmyadmin.zip'
            Upgrade.executioner(command, 0)

            command = 'unzip /usr/local/CyberCP/public/phpmyadmin.zip -d /usr/local/CyberCP/public/'
            Upgrade.executioner(command, 0)

            command = 'mv /usr/local/CyberCP/public/phpMyAdmin-*-all-languages /usr/local/CyberCP/public/phpmyadmin'
            subprocess.call(command, shell=True)

            command = 'rm -f /usr/local/CyberCP/public/phpmyadmin.zip'
            Upgrade.executioner(command, 0)

            ## Write secret phrase

            rString = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])

            data = open('/usr/local/CyberCP/public/phpmyadmin/config.sample.inc.php', 'r').readlines()

            writeToFile = open('/usr/local/CyberCP/public/phpmyadmin/config.inc.php', 'w')

            writeE = 1

            phpMyAdminContent = """
$cfg['Servers'][$i]['AllowNoPassword'] = false;
$cfg['Servers'][$i]['auth_type'] = 'signon';
$cfg['Servers'][$i]['SignonSession'] = 'SignonSession';
$cfg['Servers'][$i]['SignonURL'] = 'phpmyadminsignin.php';
$cfg['Servers'][$i]['LogoutURL'] = 'phpmyadminsignin.php?logout';
"""

            for items in data:
                if items.find('blowfish_secret') > -1:
                    writeToFile.writelines(
                        "$cfg['blowfish_secret'] = '" + rString + "'; /* YOU MUST FILL IN THIS FOR COOKIE AUTH! */\n")
                elif items.find('/* Authentication type */') > -1:
                    writeToFile.writelines(items)
                    writeToFile.write(phpMyAdminContent)
                    writeE = 0
                elif items.find("$cfg['Servers'][$i]['AllowNoPassword']") > -1:
                    writeE = 1
                else:
                    if writeE:
                        writeToFile.writelines(items)

            writeToFile.writelines("$cfg['TempDir'] = '/usr/local/CyberCP/public/phpmyadmin/tmp';\n")

            writeToFile.close()

            os.mkdir('/usr/local/CyberCP/public/phpmyadmin/tmp')

            command = 'cp /usr/local/CyberCP/plogical/phpmyadminsignin.php /usr/local/CyberCP/public/phpmyadmin/phpmyadminsignin.php'
            Upgrade.executioner(command, 0)

            passFile = "/etc/cyberpanel/mysqlPassword"

            try:
                import json
                jsonData = json.loads(open(passFile, 'r').read())

                mysqluser = jsonData['mysqluser']
                mysqlpassword = jsonData['mysqlpassword']
                mysqlport = jsonData['mysqlport']
                mysqlhost = jsonData['mysqlhost']

                command = "sed -i 's|localhost|%s|g' /usr/local/CyberCP/public/phpmyadmin/phpmyadminsignin.php" % (
                    mysqlhost)
                Upgrade.executioner(command, 0)

            except:
                pass

            os.chdir(cwd)

        except BaseException as msg:
            Upgrade.stdOut(str(msg) + " [download_install_phpmyadmin]", 0)

    @staticmethod
    def setupComposer():

        if os.path.exists('composer.sh'):
            os.remove('composer.sh')

        command = "wget https://cyberpanel.sh/composer.sh"
        Upgrade.executioner(command, 0)

        command = "chmod +x composer.sh"
        Upgrade.executioner(command, 0)

        command = "./composer.sh"
        Upgrade.executioner(command, 0)

    @staticmethod
    def downoad_and_install_raindloop():
        try:
            #######

            # if os.path.exists("/usr/local/CyberCP/public/rainloop"):
            #
            #     if os.path.exists("/usr/local/lscp/cyberpanel/rainloop/data"):
            #         pass
            #     else:
            #         command = "mv /usr/local/CyberCP/public/rainloop/data /usr/local/lscp/cyberpanel/rainloop/data"
            #         Upgrade.executioner(command, 0)
            #
            #         command = "chown -R lscpd:lscpd /usr/local/lscp/cyberpanel/rainloop/data"
            #         Upgrade.executioner(command, 0)
            #
            #     iPath = os.listdir('/usr/local/CyberCP/public/rainloop/rainloop/v/')
            #
            #     path = "/usr/local/CyberCP/public/snappymail/snappymail/v/%s/include.php" % (iPath[0])
            #
            #     data = open(path, 'r').readlines()
            #     writeToFile = open(path, 'w')
            #
            #     for items in data:
            #         if items.find("$sCustomDataPath = '';") > -1:
            #             writeToFile.writelines(
            #                 "			$sCustomDataPath = '/usr/local/lscp/cyberpanel/rainloop/data';\n")
            #         else:
            #             writeToFile.writelines(items)
            #
            #     writeToFile.close()
            #     return 0

            cwd = os.getcwd()

            if not os.path.exists("/usr/local/CyberCP/public"):
                os.mkdir("/usr/local/CyberCP/public")

            os.chdir("/usr/local/CyberCP/public")

            count = 1

            while (1):
                command = 'wget https://github.com/the-djmaze/snappymail/releases/download/v%s/snappymail-%s.zip' % (
                    Upgrade.SnappyVersion, Upgrade.SnappyVersion)
                cmd = shlex.split(command)
                res = subprocess.call(cmd)
                if res != 0:
                    count = count + 1
                    if count == 3:
                        break
                else:
                    break

            #############

            count = 0

            if os.path.exists('/usr/local/CyberCP/public/snappymail'):
                shutil.rmtree('/usr/local/CyberCP/public/snappymail')

            while (1):
                command = 'unzip snappymail-%s.zip -d /usr/local/CyberCP/public/snappymail' % (Upgrade.SnappyVersion)

                cmd = shlex.split(command)
                res = subprocess.call(cmd)
                if res != 0:
                    count = count + 1
                    if count == 3:
                        break
                else:
                    break
            try:
                os.remove("snappymail-%s.zip" % (Upgrade.SnappyVersion))
            except:
                pass

            #######

            os.chdir("/usr/local/CyberCP/public/snappymail")

            count = 0

            while (1):
                command = 'find . -type d -exec chmod 755 {} \;'
                cmd = shlex.split(command)
                res = subprocess.call(cmd)
                if res != 0:
                    count = count + 1
                    if count == 3:
                        break
                else:
                    break

            #############

            count = 0

            while (1):
                command = 'find . -type f -exec chmod 644 {} \;'
                cmd = shlex.split(command)
                res = subprocess.call(cmd)
                if res != 0:
                    count = count + 1
                    if count == 3:
                        break
                else:
                    break
            ######

            iPath = os.listdir('/usr/local/CyberCP/public/snappymail/snappymail/v/')

            path = "/usr/local/CyberCP/public/snappymail/snappymail/v/%s/include.php" % (iPath[0])

            data = open(path, 'r').readlines()
            writeToFile = open(path, 'w')

            for items in data:
                if items.find("$sCustomDataPath = '';") > -1:
                    writeToFile.writelines(
                        "			$sCustomDataPath = '/usr/local/lscp/cyberpanel/rainloop/data';\n")
                else:
                    writeToFile.writelines(items)

            writeToFile.close()

            command = "mkdir -p /usr/local/lscp/cyberpanel/rainloop/data/_data_/_default_/configs/"
            Upgrade.executioner(command, 'mkdir snappymail configs', 0)

            command = f'wget -O /usr/local/CyberCP/snappymail_cyberpanel.php  https://raw.githubusercontent.com/the-djmaze/snappymail/master/integrations/cyberpanel/install.php'
            Upgrade.executioner(command, 'verify certificate', 0)

            command = f'/usr/local/lsws/lsphp80/bin/php /usr/local/CyberCP/snappymail_cyberpanel.php'
            Upgrade.executioner(command, 'verify certificate', 0)

            # labsPath = '/usr/local/lscp/cyberpanel/rainloop/data/_data_/_default_/configs/application.ini'

            #             labsData = """[labs]
            # imap_folder_list_limit = 0
            # autocreate_system_folders = On
            # """
            #
            #             writeToFile = open(labsPath, 'a')
            #             writeToFile.write(labsData)
            #             writeToFile.close()

            includeFileOldPath = '/usr/local/CyberCP/public/snappymail/_include.php'
            includeFileNewPath = '/usr/local/CyberCP/public/snappymail/include.php'

            # if os.path.exists(includeFileOldPath):
            #     writeToFile = open(includeFileOldPath, 'a')
            #     writeToFile.write("\ndefine('APP_DATA_FOLDER_PATH', '/usr/local/lscp/cyberpanel/rainloop/data/');\n")
            #     writeToFile.close()

            # command = 'mv %s %s' % (includeFileOldPath, includeFileNewPath)
            # Upgrade.executioner(command, 'mkdir snappymail configs', 0)

            ## take care of auto create folders

            ## Disable local cert verification

            # command = "sed -i 's|verify_certificate = On|verify_certificate = Off|g' %s" % (labsPath)
            # Upgrade.executioner(command, 'verify certificate', 0)

            # labsData = open(labsPath, 'r').read()
            # labsDataLines = open(labsPath, 'r').readlines()
            #
            # if labsData.find('autocreate_system_folders') > -1:
            #     command = "sed -i 's|autocreate_system_folders = Off|autocreate_system_folders = On|g' %s" % (labsPath)
            #     Upgrade.executioner(command, 'mkdir snappymail configs', 0)
            # else:
            #     WriteToFile = open(labsPath, 'w')
            #     for lines in labsDataLines:
            #         if lines.find('[labs]') > -1:
            #             WriteToFile.write(lines)
            #             WriteToFile.write(f'autocreate_system_folders = On\n')
            #         else:
            #             WriteToFile.write(lines)
            #     WriteToFile.close()

            ##take care of imap_folder_list_limit

            # labsDataLines = open(labsPath, 'r').readlines()
            #
            # if labsData.find('imap_folder_list_limit') == -1:
            #     WriteToFile = open(labsPath, 'w')
            #     for lines in labsDataLines:
            #         if lines.find('[labs]') > -1:
            #             WriteToFile.write(lines)
            #             WriteToFile.write(f'imap_folder_list_limit = 0\n')
            #         else:
            #             WriteToFile.write(lines)
            #     WriteToFile.close()

            ### now download and install actual plugin

            #             command = f'mkdir /usr/local/lscp/cyberpanel/rainloop/data/_data_/_default_/plugins/mailbox-detect'
            #             Upgrade.executioner(command, 'verify certificate', 0)
            #
            #             command = f'chmod 700 /usr/local/lscp/cyberpanel/rainloop/data/_data_/_default_/plugins/mailbox-detect'
            #             Upgrade.executioner(command, 'verify certificate', 0)
            #
            #             command = f'chown lscpd:lscpd /usr/local/lscp/cyberpanel/rainloop/data/_data_/_default_/plugins/mailbox-detect'
            #             Upgrade.executioner(command, 'verify certificate', 0)
            #
            #             command = f'wget -O /usr/local/lscp/cyberpanel/rainloop/data/_data_/_default_/plugins/mailbox-detect/index.php https://raw.githubusercontent.com/the-djmaze/snappymail/master/plugins/mailbox-detect/index.php'
            #             Upgrade.executioner(command, 'verify certificate', 0)
            #
            #             command = f'chmod 644 /usr/local/lscp/cyberpanel/rainloop/data/_data_/_default_/plugins/mailbox-detect/index.php'
            #             Upgrade.executioner(command, 'verify certificate', 0)
            #
            #             command = f'chown lscpd:lscpd /usr/local/lscp/cyberpanel/rainloop/data/_data_/_default_/plugins/mailbox-detect/index.php'
            #             Upgrade.executioner(command, 'verify certificate', 0)
            #
            #             ### Enable plugins and enable mailbox creation plugin
            #
            #             labsDataLines = open(labsPath, 'r').readlines()
            #             PluginsActivator = 0
            #             WriteToFile = open(labsPath, 'w')
            #
            #
            #             for lines in labsDataLines:
            #                 if lines.find('[plugins]') > -1:
            #                     PluginsActivator = 1
            #                     WriteToFile.write(lines)
            #                 elif PluginsActivator and lines.find('enable = ') > -1:
            #                     WriteToFile.write(f'enable = On\n')
            #                 elif PluginsActivator and lines.find('enabled_list = ') > -1:
            #                     WriteToFile.write(f'enabled_list = "mailbox-detect"\n')
            #                 elif PluginsActivator == 1 and lines.find('[defaults]') > -1:
            #                     PluginsActivator = 0
            #                     WriteToFile.write(lines)
            #                 else:
            #                     WriteToFile.write(lines)
            #             WriteToFile.close()
            #
            #             ## enable auto create in the enabled plugin
            #             PluginsFilePath = '/usr/local/lscp/cyberpanel/rainloop/data/_data_/_default_/configs/plugin-mailbox-detect.json'
            #
            #             WriteToFile = open(PluginsFilePath, 'w')
            #             WriteToFile.write("""{
            #     "plugin": {
            #         "autocreate_system_folders": true
            #     }
            # }
            # """)
            #             WriteToFile.close()
            #
            #             command = f'chown lscpd:lscpd {PluginsFilePath}'
            #             Upgrade.executioner(command, 'verify certificate', 0)
            #
            #             command = f'chmod 600 {PluginsFilePath}'
            #             Upgrade.executioner(command, 'verify certificate', 0)

            os.chdir(cwd)

        except BaseException as msg:
            Upgrade.stdOut(str(msg) + " [downoad_and_install_raindloop]", 0)

        return 1

    @staticmethod
    def downloadLink():
        try:
            version_number = VERSION
            version_build = str(BUILD)

            try:
                Content = {"version":version_number,"build":version_build}
                path = "/usr/local/CyberCP/version.txt"
                writeToFile = open(path, 'w')
                writeToFile.write(json.dumps(Content))
                writeToFile.close()
            except:
                pass

            return (version_number + "." + version_build + ".tar.gz")
        except BaseException as msg:
            Upgrade.stdOut(str(msg) + ' [downloadLink]')
            os._exit(0)

    @staticmethod
    def setupCLI():
        try:

            command = "ln -s /usr/local/CyberCP/cli/cyberPanel.py /usr/bin/cyberpanel"
            Upgrade.executioner(command, 'CLI Symlink', 0)

            command = "chmod +x /usr/local/CyberCP/cli/cyberPanel.py"
            Upgrade.executioner(command, 'CLI Permissions', 0)

        except OSError as msg:
            Upgrade.stdOut(str(msg) + " [setupCLI]")
            return 0

    @staticmethod
    def staticContent():

        command = "rm -rf /usr/local/CyberCP/public/static"
        Upgrade.executioner(command, 'Remove old static content', 0)

        ##

        if not os.path.exists("/usr/local/CyberCP/public"):
            os.mkdir("/usr/local/CyberCP/public")

        cwd = os.getcwd()

        os.chdir('/usr/local/CyberCP')

        command = '/usr/local/CyberPanel/bin/python manage.py collectstatic --noinput --clear'
        Upgrade.executioner(command, 'Remove old static content', 0)

        os.chdir(cwd)

        shutil.move("/usr/local/CyberCP/static", "/usr/local/CyberCP/public/")

    @staticmethod
    def upgradeVersion():
        try:

            import django
            os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CyberCP.settings")
            django.setup()
            from baseTemplate.models import version

            vers = version.objects.get(pk=1)
            vers.currentVersion = VERSION
            vers.build = str(BUILD)
            vers.save()
        except:
            pass

    @staticmethod
    def setupConnection(db=None):
        try:
            passFile = "/etc/cyberpanel/mysqlPassword"

            f = open(passFile)
            data = f.read()
            password = data.split('\n', 1)[0]

            if db == None:
                conn = mysql.connect(user='root', passwd=password)
            else:
                try:
                    conn = mysql.connect(db=db, user='root', passwd=password)
                except:
                    try:
                        conn = mysql.connect(host='127.0.0.1', port=3307, db=db, user='root', passwd=password)
                    except:
                        dbUser = settings.DATABASES['default']['USER']
                        password = settings.DATABASES['default']['PASSWORD']
                        host = settings.DATABASES['default']['HOST']
                        port = settings.DATABASES['default']['PORT']

                        if port == '':
                            conn = mysql.connect(host=host, port=3306, db=db, user=dbUser, passwd=password)
                        else:
                            conn = mysql.connect(host=host, port=int(port), db=db, user=dbUser, passwd=password)

            cursor = conn.cursor()
            return conn, cursor

        except BaseException as msg:
            Upgrade.stdOut(str(msg))
            return 0, 0

    @staticmethod
    def applyLoginSystemMigrations():
        try:

            connection, cursor = Upgrade.setupConnection('cyberpanel')

            try:
                cursor.execute(
                    'CREATE TABLE `baseTemplate_cyberpanelcosmetic` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `MainDashboardCSS` longtext NOT NULL)')
            except:
                pass

            try:
                cursor.execute(
                    'CREATE TABLE `loginSystem_acl` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `name` varchar(50) NOT NULL UNIQUE, `adminStatus` integer NOT NULL DEFAULT 0, `versionManagement` integer NOT NULL DEFAULT 0, `createNewUser` integer NOT NULL DEFAULT 0, `deleteUser` integer NOT NULL DEFAULT 0, `resellerCenter` integer NOT NULL DEFAULT 0, `changeUserACL` integer NOT NULL DEFAULT 0, `createWebsite` integer NOT NULL DEFAULT 0, `modifyWebsite` integer NOT NULL DEFAULT 0, `suspendWebsite` integer NOT NULL DEFAULT 0, `deleteWebsite` integer NOT NULL DEFAULT 0, `createPackage` integer NOT NULL DEFAULT 0, `deletePackage` integer NOT NULL DEFAULT 0, `modifyPackage` integer NOT NULL DEFAULT 0, `createDatabase` integer NOT NULL DEFAULT 0, `deleteDatabase` integer NOT NULL DEFAULT 0, `listDatabases` integer NOT NULL DEFAULT 0, `createNameServer` integer NOT NULL DEFAULT 0, `createDNSZone` integer NOT NULL DEFAULT 0, `deleteZone` integer NOT NULL DEFAULT 0, `addDeleteRecords` integer NOT NULL DEFAULT 0, `createEmail` integer NOT NULL DEFAULT 0, `deleteEmail` integer NOT NULL DEFAULT 0, `emailForwarding` integer NOT NULL DEFAULT 0, `changeEmailPassword` integer NOT NULL DEFAULT 0, `dkimManager` integer NOT NULL DEFAULT 0, `createFTPAccount` integer NOT NULL DEFAULT 0, `deleteFTPAccount` integer NOT NULL DEFAULT 0, `listFTPAccounts` integer NOT NULL DEFAULT 0, `createBackup` integer NOT NULL DEFAULT 0, `restoreBackup` integer NOT NULL DEFAULT 0, `addDeleteDestinations` integer NOT NULL DEFAULT 0, `scheduleBackups` integer NOT NULL DEFAULT 0, `remoteBackups` integer NOT NULL DEFAULT 0, `manageSSL` integer NOT NULL DEFAULT 0, `hostnameSSL` integer NOT NULL DEFAULT 0, `mailServerSSL` integer NOT NULL DEFAULT 0)')
            except:
                pass

            try:
                cursor.execute('ALTER TABLE loginSystem_administrator ADD token varchar(500)')
            except:
                pass

            try:
                cursor.execute("ALTER TABLE loginSystem_administrator ADD secretKey varchar(50) DEFAULT 'None'")
            except:
                pass

            try:
                cursor.execute('alter table databases_databases drop index dbUser;')
            except:
                pass

            try:
                cursor.execute("ALTER TABLE loginSystem_administrator ADD state varchar(15) DEFAULT 'ACTIVE'")
            except:
                pass

            try:
                cursor.execute('ALTER TABLE loginSystem_administrator ADD securityLevel integer DEFAULT 1')
            except:
                pass

            try:
                cursor.execute('ALTER TABLE loginSystem_administrator ADD defaultSite integer DEFAULT 0')
            except:
                pass

            try:
                cursor.execute('ALTER TABLE loginSystem_administrator ADD twoFA integer DEFAULT 0')
            except:
                pass

            try:
                cursor.execute('ALTER TABLE loginSystem_administrator ADD api integer')
            except:
                pass

            try:
                cursor.execute('ALTER TABLE loginSystem_administrator ADD acl_id integer')
            except:
                pass
            try:
                cursor.execute(
                    'ALTER TABLE loginSystem_administrator ADD FOREIGN KEY (acl_id) REFERENCES loginSystem_acl(id)')
            except:
                pass

            try:
                cursor.execute("insert into loginSystem_acl (id, name, adminStatus) values (1,'admin',1)")
            except:
                pass

            try:
                cursor.execute(
                    "insert into loginSystem_acl (id, name, adminStatus, createNewUser, deleteUser, createWebsite, resellerCenter, modifyWebsite, suspendWebsite, deleteWebsite, createPackage, deletePackage, modifyPackage, createNameServer, restoreBackup) values (2,'reseller',0,1,1,1,1,1,1,1,1,1,1,1,1)")
            except:
                pass
            try:
                cursor.execute(
                    "insert into loginSystem_acl (id, name, createDatabase, deleteDatabase, listDatabases, createDNSZone, deleteZone, addDeleteRecords, createEmail, deleteEmail, emailForwarding, changeEmailPassword, dkimManager, createFTPAccount, deleteFTPAccount, listFTPAccounts, createBackup, manageSSL) values (3,'user', 1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1)")
            except:
                pass

            try:
                cursor.execute("UPDATE loginSystem_administrator SET  acl_id = 1 where userName = 'admin'")
            except:
                pass

            try:
                cursor.execute('ALTER TABLE loginSystem_acl ADD config longtext')
            except:
                pass

            try:
                cursor.execute("UPDATE loginSystem_acl SET config = '%s' where name = 'admin'" % (Upgrade.AdminACL))
            except BaseException as msg:
                print(str(msg))
                try:
                    import sleep
                except:
                    from time import sleep
                from time import sleep
                sleep(10)

            try:
                cursor.execute(
                    "UPDATE loginSystem_acl SET config = '%s' where name = 'reseller'" % (Upgrade.ResellerACL))
            except:
                pass

            try:
                cursor.execute("UPDATE loginSystem_acl SET config = '%s' where name = 'user'" % (Upgrade.UserACL))
            except:
                pass

            try:
                cursor.execute("alter table loginSystem_administrator drop initUserAccountsLimit")
            except:
                pass

            try:
                cursor.execute(
                    "CREATE TABLE `websiteFunctions_aliasdomains` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `aliasDomain` varchar(75) NOT NULL)")
            except:
                pass
            try:
                cursor.execute("ALTER TABLE `websiteFunctions_aliasdomains` ADD COLUMN `master_id` integer NOT NULL")
            except:
                pass
            try:
                cursor.execute(
                    "ALTER TABLE `websiteFunctions_aliasdomains` ADD CONSTRAINT `websiteFunctions_ali_master_id_726c433d_fk_websiteFu` FOREIGN KEY (`master_id`) REFERENCES `websiteFunctions_websites` (`id`)")
            except:
                pass

            try:
                cursor.execute('ALTER TABLE websiteFunctions_websites ADD config longtext')
            except:
                pass

            try:
                cursor.execute("ALTER TABLE websiteFunctions_websites MODIFY externalApp varchar(30)")
            except:
                pass

            try:
                cursor.execute("ALTER TABLE emailMarketing_smtphosts MODIFY userName varchar(200)")
            except:
                pass

            try:
                cursor.execute("ALTER TABLE emailMarketing_smtphosts MODIFY password varchar(200)")
            except:
                pass

            try:
                cursor.execute("ALTER TABLE websiteFunctions_backups MODIFY fileName varchar(200)")
            except:
                pass

            try:
                cursor.execute("ALTER TABLE loginSystem_acl ADD COLUMN listUsers INT DEFAULT 0;")
            except:
                pass

            try:
                cursor.execute("ALTER TABLE loginSystem_acl ADD COLUMN listEmails INT DEFAULT 1;")
            except:
                pass

            try:
                cursor.execute("ALTER TABLE loginSystem_acl ADD COLUMN listPackages INT DEFAULT 0;")
            except:
                pass

            query = """CREATE TABLE `websiteFunctions_normalbackupdests` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(25) NOT NULL,
  `config` longtext NOT NULL,
  PRIMARY KEY (`id`)
)"""
            try:
                cursor.execute(query)
            except:
                pass

            query = """CREATE TABLE `cloudAPI_wpdeployments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `config` longtext NOT NULL,
  `owner_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `cloudAPI_wpdeploymen_owner_id_506ddf01_fk_websiteFu` (`owner_id`),
  CONSTRAINT `cloudAPI_wpdeploymen_owner_id_506ddf01_fk_websiteFu` FOREIGN KEY (`owner_id`) REFERENCES `websiteFunctions_websites` (`id`)
)"""

            try:
                cursor.execute(query)
            except:
                pass

            query = """CREATE TABLE `websiteFunctions_normalbackupjobs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(25) NOT NULL,
  `config` longtext NOT NULL,
  `owner_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `websiteFunctions_nor_owner_id_3a7a13db_fk_websiteFu` (`owner_id`),
  CONSTRAINT `websiteFunctions_nor_owner_id_3a7a13db_fk_websiteFu` FOREIGN KEY (`owner_id`) REFERENCES `websiteFunctions_normalbackupdests` (`id`)
)"""

            try:
                cursor.execute(query)
            except:
                pass

            query = """CREATE TABLE `websiteFunctions_normalbackupsites` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `domain_id` int(11) NOT NULL,
  `owner_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `websiteFunctions_nor_domain_id_c03362bc_fk_websiteFu` (`domain_id`),
  KEY `websiteFunctions_nor_owner_id_c6ece6cc_fk_websiteFu` (`owner_id`),
  CONSTRAINT `websiteFunctions_nor_domain_id_c03362bc_fk_websiteFu` FOREIGN KEY (`domain_id`) REFERENCES `websiteFunctions_websites` (`id`),
  CONSTRAINT `websiteFunctions_nor_owner_id_c6ece6cc_fk_websiteFu` FOREIGN KEY (`owner_id`) REFERENCES `websiteFunctions_normalbackupjobs` (`id`)
)"""

            try:
                cursor.execute(query)
            except:
                pass

            query = """CREATE TABLE `websiteFunctions_normalbackupjoblogs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `status` int(11) NOT NULL,
  `message` longtext NOT NULL,
  `owner_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `websiteFunctions_nor_owner_id_69403e73_fk_websiteFu` (`owner_id`),
  CONSTRAINT `websiteFunctions_nor_owner_id_69403e73_fk_websiteFu` FOREIGN KEY (`owner_id`) REFERENCES `websiteFunctions_normalbackupjobs` (`id`)
)"""

            try:
                cursor.execute(query)
            except:
                pass

            try:
                cursor.execute('ALTER TABLE e_users ADD DiskUsage varchar(200)')
            except:
                pass

            try:
                cursor.execute(
                    'CREATE TABLE `websiteFunctions_wpplugins` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `Name` varchar(255) NOT NULL, `config` longtext NOT NULL, `owner_id` integer NOT NULL)')
            except:
                pass

            try:
                cursor.execute(
                    'ALTER TABLE `websiteFunctions_wpplugins` ADD CONSTRAINT `websiteFunctions_wpp_owner_id_493a02c7_fk_loginSyst` FOREIGN KEY (`owner_id`) REFERENCES `loginSystem_administrator` (`id`)')
            except:
                pass

            try:
                cursor.execute(
                    'CREATE TABLE `websiteFunctions_wpsites` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `title` varchar(255) NOT NULL, `path` varchar(255) NOT NULL, `FinalURL` varchar(255) NOT NULL, `AutoUpdates` varchar(100) NOT NULL, `PluginUpdates` varchar(15) NOT NULL, `ThemeUpdates` varchar(15) NOT NULL, `date` datetime(6) NOT NULL, `WPLockState` integer NOT NULL, `owner_id` integer NOT NULL)')
            except:
                pass

            try:
                cursor.execute(
                    'ALTER TABLE `websiteFunctions_wpsites` ADD CONSTRAINT `websiteFunctions_wps_owner_id_6d67df2a_fk_websiteFu` FOREIGN KEY (`owner_id`) REFERENCES `websiteFunctions_websites` (`id`)')
            except:
                pass

            try:
                cursor.execute(
                    'CREATE TABLE `websiteFunctions_wpstaging` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `owner_id` integer NOT NULL, `wpsite_id` integer NOT NULL)')
            except:
                pass

            try:
                cursor.execute(
                    'ALTER TABLE `websiteFunctions_wpstaging` ADD CONSTRAINT `websiteFunctions_wps_owner_id_543d8aec_fk_websiteFu` FOREIGN KEY (`owner_id`) REFERENCES `websiteFunctions_wpsites` (`id`);')
            except:
                pass

            try:
                cursor.execute(
                    'ALTER TABLE `websiteFunctions_wpstaging` ADD CONSTRAINT `websiteFunctions_wps_wpsite_id_82843593_fk_websiteFu` FOREIGN KEY (`wpsite_id`) REFERENCES `websiteFunctions_wpsites` (`id`)')
            except:
                pass

            try:
                cursor.execute(
                    "CREATE TABLE `websiteFunctions_wpsitesbackup` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `WPSiteID` integer NOT NULL, `WebsiteID` integer NOT NULL, `config` longtext NOT NULL, `owner_id` integer NOT NULL); ")
            except:
                pass

            try:
                cursor.execute(
                    "ALTER TABLE `websiteFunctions_wpsitesbackup` ADD CONSTRAINT `websiteFunctions_wps_owner_id_8a8dd0c5_fk_loginSyst` FOREIGN KEY (`owner_id`) REFERENCES `loginSystem_administrator` (`id`); ")
            except:
                pass

            query = """CREATE TABLE `websiteFunctions_remotebackupconfig` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `configtype` varchar(255) NOT NULL,
  `config` longtext NOT NULL,
  `owner_id` int(11) NOT NULL,
  PRIMARY KEY (`id`)
)"""
            try:
                cursor.execute(query)
            except:
                pass

            query = """CREATE TABLE `websiteFunctions_remotebackupschedule` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `Name` varchar(255) NOT NULL,
  `timeintervel` varchar(200) NOT NULL,
  `fileretention` varchar(200) NOT NULL,
  `lastrun` varchar(200) NOT NULL,
  `config` longtext NOT NULL,
  `RemoteBackupConfig_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `websiteFunctions_rem_RemoteBackupConfig_i_224c46fb_fk_websiteFu` (`RemoteBackupConfig_id`),
  CONSTRAINT `websiteFunctions_rem_RemoteBackupConfig_i_224c46fb_fk_websiteFu` FOREIGN KEY (`RemoteBackupConfig_id`) REFERENCES `websiteFunctions_remotebackupconfig` (`id`)
)"""
            try:
                cursor.execute(query)
            except:
                pass

            query = """CREATE TABLE `websiteFunctions_remotebackupsites` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `WPsites` int(11) DEFAULT NULL,
  `database` int(11) DEFAULT NULL,
  `owner_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `websiteFunctions_rem_owner_id_d6c4475a_fk_websiteFu` (`owner_id`),
  CONSTRAINT `websiteFunctions_rem_owner_id_d6c4475a_fk_websiteFu` FOREIGN KEY (`owner_id`) REFERENCES `websiteFunctions_remotebackupschedule` (`id`)
)"""
            try:
                cursor.execute(query)
            except:
                pass

            query = """
CREATE TABLE `websiteFunctions_backupsv2` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `fileName` varchar(255) NOT NULL, `status` integer NOT NULL, `timeStamp` varchar(255) NOT NULL, `BasePath` longtext NOT NULL, `website_id` integer NOT NULL);            
"""
            try:
                cursor.execute(query)
            except:
                pass

            query = "ALTER TABLE `websiteFunctions_backupsv2` ADD CONSTRAINT `websiteFunctions_bac_website_id_3a777e68_fk_websiteFu` FOREIGN KEY (`website_id`) REFERENCES `websiteFunctions_websites` (`id`);"

            try:
                cursor.execute(query)
            except:
                pass

            query = "ALTER TABLE `websiteFunctions_backupslogsv2` ADD CONSTRAINT `websiteFunctions_bac_owner_id_9e884ff9_fk_websiteFu` FOREIGN KEY (`owner_id`) REFERENCES `websiteFunctions_backupsv2` (`id`);"

            try:
                cursor.execute(query)
            except:
                pass

            query = "CREATE TABLE `websiteFunctions_backupslogsv2` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `timeStamp` varchar(255) NOT NULL, `message` longtext NOT NULL, `owner_id` integer NOT NULL);"

            try:
                cursor.execute(query)
            except:
                pass

            query = "ALTER TABLE `websiteFunctions_backupslogsv2` ADD CONSTRAINT `websiteFunctions_bac_owner_id_9e884ff9_fk_websiteFu` FOREIGN KEY (`owner_id`) REFERENCES `websiteFunctions_backupsv2` (`id`);"

            try:
                cursor.execute(query)
            except:
                pass

            try:
                cursor.execute("ALTER TABLE websiteFunctions_websites ADD COLUMN BackupLock INT DEFAULT 0;")
            except:
                pass

            ### update ftp issue for ubuntu 22

            try:
                cursor.execute(
                    'ALTER TABLE `users` CHANGE `Password` `Password` VARCHAR(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL; ')
            except:
                pass

            query = "CREATE TABLE `IncBackups_oneclickbackups` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `planName` varchar(100) NOT NULL, `months` varchar(100) NOT NULL, `price` varchar(100) NOT NULL, `customer` varchar(255) NOT NULL, `subscription` varchar(255) NOT NULL UNIQUE, `sftpUser` varchar(100) NOT NULL, `config` longtext NOT NULL, `date` datetime(6) NOT NULL, `state` integer NOT NULL, `owner_id` integer NOT NULL);"
            try:
                cursor.execute(query)
            except:
                pass

            query = 'ALTER TABLE `IncBackups_oneclickbackups` ADD CONSTRAINT `IncBackups_oneclickb_owner_id_7b4250a4_fk_loginSyst` FOREIGN KEY (`owner_id`) REFERENCES `loginSystem_administrator` (`id`);'
            try:
                cursor.execute(query)
            except:
                pass

            if Upgrade.FindOperatingSytem() == Ubuntu22:
                ### If ftp not installed then upgrade will fail so this command should not do exit

                command = "sed -i 's/MYSQLCrypt md5/MYSQLCrypt crypt/g' /etc/pure-ftpd/db/mysql.conf"
                Upgrade.executioner(command, command, 0)

                command = "systemctl restart pure-ftpd-mysql.service"
                Upgrade.executioner(command, command, 0)

            try:
                clAPVersion = Upgrade.FetchCloudLinuxAlmaVersionVersion()
                type = clAPVersion.split('-')[0]
                version = int(clAPVersion.split('-')[1])

                if type == 'al' and version >= 90:
                    command = "sed -i 's/MYSQLCrypt md5/MYSQLCrypt crypt/g' /etc/pure-ftpd/pureftpd-mysql.conf"
                    Upgrade.executioner(command, command, 0)
            except:
                pass

            try:
                connection.close()
            except:
                pass

        except OSError as msg:
            Upgrade.stdOut(str(msg) + " [applyLoginSystemMigrations]")

    @staticmethod
    def s3BackupMigrations():
        try:

            connection, cursor = Upgrade.setupConnection('cyberpanel')

            query = """CREATE TABLE `s3Backups_backupplan` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `bucket` varchar(50) NOT NULL,
  `freq` varchar(50) NOT NULL,
  `retention` int(11) NOT NULL,
  `type` varchar(5) NOT NULL,
  `lastRun` varchar(50) NOT NULL,
  `owner_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `s3Backups_backupplan_owner_id_7d058ced_fk_loginSyst` (`owner_id`),
  CONSTRAINT `s3Backups_backupplan_owner_id_7d058ced_fk_loginSyst` FOREIGN KEY (`owner_id`) REFERENCES `loginSystem_administrator` (`id`)
)"""

            try:
                cursor.execute(query)
            except:
                pass

            try:
                cursor.execute('ALTER TABLE s3Backups_backupplan ADD config longtext')
            except:
                pass

            query = """CREATE TABLE `s3Backups_websitesinplan` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `domain` varchar(100) NOT NULL,
  `owner_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `s3Backups_websitesin_owner_id_0e9a4fe3_fk_s3Backups` (`owner_id`),
  CONSTRAINT `s3Backups_websitesin_owner_id_0e9a4fe3_fk_s3Backups` FOREIGN KEY (`owner_id`) REFERENCES `s3Backups_backupplan` (`id`)
)"""

            try:
                cursor.execute(query)
            except:
                pass

            query = """CREATE TABLE `s3Backups_backuplogs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `timeStamp` varchar(200) NOT NULL,
  `level` varchar(5) NOT NULL,
  `msg` varchar(500) NOT NULL,
  `owner_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `s3Backups_backuplogs_owner_id_7b4653af_fk_s3Backups` (`owner_id`),
  CONSTRAINT `s3Backups_backuplogs_owner_id_7b4653af_fk_s3Backups` FOREIGN KEY (`owner_id`) REFERENCES `s3Backups_backupplan` (`id`)
)"""

            try:
                cursor.execute(query)
            except:
                pass

            query = """CREATE TABLE `s3Backups_backupplando` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `bucket` varchar(50) NOT NULL,
  `freq` varchar(50) NOT NULL,
  `retention` int(11) NOT NULL,
  `type` varchar(5) NOT NULL,
  `region` varchar(5) NOT NULL,
  `lastRun` varchar(50) NOT NULL,
  `owner_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `s3Backups_backupplan_owner_id_1a3ec86d_fk_loginSyst` (`owner_id`),
  CONSTRAINT `s3Backups_backupplan_owner_id_1a3ec86d_fk_loginSyst` FOREIGN KEY (`owner_id`) REFERENCES `loginSystem_administrator` (`id`)
)"""

            try:
                cursor.execute(query)
            except:
                pass

            query = """CREATE TABLE `s3Backups_websitesinplando` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `domain` varchar(100) NOT NULL,
  `owner_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `s3Backups_websitesin_owner_id_cef3ea04_fk_s3Backups` (`owner_id`),
  CONSTRAINT `s3Backups_websitesin_owner_id_cef3ea04_fk_s3Backups` FOREIGN KEY (`owner_id`) REFERENCES `s3Backups_backupplando` (`id`)
)"""

            try:
                cursor.execute(query)
            except:
                pass

            query = """CREATE TABLE `s3Backups_backuplogsdo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `timeStamp` varchar(200) NOT NULL,
  `level` varchar(5) NOT NULL,
  `msg` varchar(500) NOT NULL,
  `owner_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `s3Backups_backuplogs_owner_id_c7cb5872_fk_s3Backups` (`owner_id`),
  CONSTRAINT `s3Backups_backuplogs_owner_id_c7cb5872_fk_s3Backups` FOREIGN KEY (`owner_id`) REFERENCES `s3Backups_backupplando` (`id`)
)"""

            try:
                cursor.execute(query)
            except:
                pass

            ##

            query = """CREATE TABLE `s3Backups_minionodes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `endPointURL` varchar(200) NOT NULL,
  `accessKey` varchar(200) NOT NULL,
  `secretKey` varchar(200) NOT NULL,
  `owner_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `endPointURL` (`endPointURL`),
  UNIQUE KEY `accessKey` (`accessKey`),
  KEY `s3Backups_minionodes_owner_id_e50993d9_fk_loginSyst` (`owner_id`),
  CONSTRAINT `s3Backups_minionodes_owner_id_e50993d9_fk_loginSyst` FOREIGN KEY (`owner_id`) REFERENCES `loginSystem_administrator` (`id`)
)"""

            try:
                cursor.execute(query)
            except:
                pass

            query = """CREATE TABLE `s3Backups_backupplanminio` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `freq` varchar(50) NOT NULL,
  `retention` int(11) NOT NULL,
  `lastRun` varchar(50) NOT NULL,
  `minioNode_id` int(11) NOT NULL,
  `owner_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `s3Backups_backupplan_minioNode_id_a4eaf917_fk_s3Backups` (`minioNode_id`),
  KEY `s3Backups_backupplan_owner_id_d6830e67_fk_loginSyst` (`owner_id`),
  CONSTRAINT `s3Backups_backupplan_minioNode_id_a4eaf917_fk_s3Backups` FOREIGN KEY (`minioNode_id`) REFERENCES `s3Backups_minionodes` (`id`),
  CONSTRAINT `s3Backups_backupplan_owner_id_d6830e67_fk_loginSyst` FOREIGN KEY (`owner_id`) REFERENCES `loginSystem_administrator` (`id`)
)"""

            try:
                cursor.execute(query)
            except:
                pass

            query = """CREATE TABLE `s3Backups_websitesinplanminio` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `domain` varchar(100) NOT NULL,
  `owner_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `s3Backups_websitesin_owner_id_224ce049_fk_s3Backups` (`owner_id`),
  CONSTRAINT `s3Backups_websitesin_owner_id_224ce049_fk_s3Backups` FOREIGN KEY (`owner_id`) REFERENCES `s3Backups_backupplanminio` (`id`)
)"""

            try:
                cursor.execute(query)
            except:
                pass

            query = """CREATE TABLE `s3Backups_backuplogsminio` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `timeStamp` varchar(200) NOT NULL,
  `level` varchar(5) NOT NULL,
  `msg` varchar(500) NOT NULL,
  `owner_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `s3Backups_backuplogs_owner_id_f19e1736_fk_s3Backups` (`owner_id`),
  CONSTRAINT `s3Backups_backuplogs_owner_id_f19e1736_fk_s3Backups` FOREIGN KEY (`owner_id`) REFERENCES `s3Backups_backupplanminio` (`id`)
)"""

            try:
                cursor.execute(query)
            except:
                pass

            try:
                connection.close()
            except:
                pass

        except OSError as msg:
            Upgrade.stdOut(str(msg) + " [applyLoginSystemMigrations]")

    @staticmethod
    def mailServerMigrations():
        try:
            connection, cursor = Upgrade.setupConnection('cyberpanel')

            try:
                cursor.execute(
                    'ALTER TABLE `e_domains` ADD COLUMN `childOwner_id` integer')
            except:
                pass

            try:
                cursor.execute(
                    'ALTER TABLE e_users ADD mail varchar(200)')
            except:
                pass

            try:
                cursor.execute(
                    'ALTER TABLE e_users MODIFY password varchar(200)')
            except:
                pass

            try:
                cursor.execute(
                    'ALTER TABLE e_forwardings DROP PRIMARY KEY;ALTER TABLE e_forwardings ADD id INT AUTO_INCREMENT PRIMARY KEY')
            except:
                pass

            query = """CREATE TABLE `emailPremium_domainlimits` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `limitStatus` int(11) NOT NULL,
  `monthlyLimit` int(11) NOT NULL,
  `monthlyUsed` int(11) NOT NULL,
  `domain_id` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `emailPremium_domainlimits_domain_id_303ab297_fk_e_domains_domain` (`domain_id`),
  CONSTRAINT `emailPremium_domainlimits_domain_id_303ab297_fk_e_domains_domain` FOREIGN KEY (`domain_id`) REFERENCES `e_domains` (`domain`)
)"""
            try:
                cursor.execute(query)
            except:
                pass

            query = """CREATE TABLE `emailPremium_emaillimits` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `limitStatus` int(11) NOT NULL,
  `monthlyLimits` int(11) NOT NULL,
  `monthlyUsed` int(11) NOT NULL,
  `hourlyLimit` int(11) NOT NULL,
  `hourlyUsed` int(11) NOT NULL,
  `emailLogs` int(11) NOT NULL,
  `email_id` varchar(80) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `emailPremium_emaillimits_email_id_1c111df5_fk_e_users_email` (`email_id`),
  CONSTRAINT `emailPremium_emaillimits_email_id_1c111df5_fk_e_users_email` FOREIGN KEY (`email_id`) REFERENCES `e_users` (`email`)
)"""
            try:
                cursor.execute(query)
            except:
                pass

            query = """CREATE TABLE `emailPremium_emaillogs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `destination` varchar(200) NOT NULL,
  `timeStamp` varchar(200) NOT NULL,
  `email_id` varchar(80) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `emailPremium_emaillogs_email_id_9ef49552_fk_e_users_email` (`email_id`),
  CONSTRAINT `emailPremium_emaillogs_email_id_9ef49552_fk_e_users_email` FOREIGN KEY (`email_id`) REFERENCES `e_users` (`email`)
)"""
            try:
                cursor.execute(query)
            except:
                pass

            try:
                connection.close()
            except:
                pass
        except:
            pass

    @staticmethod
    def emailMarketingMigrationsa():
        try:
            connection, cursor = Upgrade.setupConnection('cyberpanel')

            query = """CREATE TABLE `emailMarketing_emailmarketing` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `userName` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `userName` (`userName`)
)"""
            try:
                cursor.execute(query)
            except:
                pass

            query = """CREATE TABLE `emailMarketing_emaillists` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `listName` varchar(50) NOT NULL,
  `dateCreated` varchar(200) NOT NULL,
  `owner_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `listName` (`listName`),
  KEY `emailMarketing_email_owner_id_bf1b4530_fk_websiteFu` (`owner_id`),
  CONSTRAINT `emailMarketing_email_owner_id_bf1b4530_fk_websiteFu` FOREIGN KEY (`owner_id`) REFERENCES `websiteFunctions_websites` (`id`)
)"""
            try:
                cursor.execute(query)
            except:
                pass

            query = 'ALTER TABLE emailMarketing_emaillists ADD COLUMN verified INT DEFAULT 0'

            try:
                cursor.execute(query)
            except:
                pass

            query = 'ALTER TABLE emailMarketing_emaillists ADD COLUMN notVerified INT DEFAULT 0'

            try:
                cursor.execute(query)
            except:
                pass

            query = """CREATE TABLE `emailMarketing_emailsinlist` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(50) NOT NULL,
  `firstName` varchar(20) NOT NULL,
  `lastName` varchar(20) NOT NULL,
  `verificationStatus` varchar(100) NOT NULL,
  `dateCreated` varchar(200) NOT NULL,
  `owner_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `emailMarketing_email_owner_id_c5c27005_fk_emailMark` (`owner_id`),
  CONSTRAINT `emailMarketing_email_owner_id_c5c27005_fk_emailMark` FOREIGN KEY (`owner_id`) REFERENCES `emailMarketing_emaillists` (`id`)
)"""

            try:
                cursor.execute(query)
            except:
                pass

            query = """CREATE TABLE `emailMarketing_smtphosts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `host` varchar(150) NOT NULL,
  `port` varchar(10) NOT NULL,
  `userName` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL,
  `owner_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `host` (`host`),
  KEY `emailMarketing_smtph_owner_id_8b2d4ac7_fk_loginSyst` (`owner_id`),
  CONSTRAINT `emailMarketing_smtph_owner_id_8b2d4ac7_fk_loginSyst` FOREIGN KEY (`owner_id`) REFERENCES `loginSystem_administrator` (`id`)
)"""

            try:
                cursor.execute(query)
            except:
                pass

            query = """CREATE TABLE `emailMarketing_emailtemplate` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `subject` varchar(1000) NOT NULL,
  `fromName` varchar(100) NOT NULL,
  `fromEmail` varchar(150) NOT NULL,
  `replyTo` varchar(150) NOT NULL,
  `emailMessage` varchar(30000) NOT NULL,
  `owner_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `emailMarketing_email_owner_id_d27e1d00_fk_loginSyst` (`owner_id`),
  CONSTRAINT `emailMarketing_email_owner_id_d27e1d00_fk_loginSyst` FOREIGN KEY (`owner_id`) REFERENCES `loginSystem_administrator` (`id`)
)"""

            try:
                cursor.execute(query)
            except:
                pass

            query = """CREATE TABLE `emailMarketing_emailjobs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` varchar(200) NOT NULL,
  `host` varchar(1000) NOT NULL,
  `totalEmails` int(11) NOT NULL,
  `sent` int(11) NOT NULL,
  `failed` int(11) NOT NULL,
  `owner_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `emailMarketing_email_owner_id_73ee4827_fk_emailMark` (`owner_id`),
  CONSTRAINT `emailMarketing_email_owner_id_73ee4827_fk_emailMark` FOREIGN KEY (`owner_id`) REFERENCES `emailMarketing_emailtemplate` (`id`)
)"""

            try:
                cursor.execute(query)
            except:
                pass

            query = """CREATE TABLE `mailServer_pipeprograms` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `source` varchar(80) NOT NULL,
  `destination` longtext NOT NULL,
  PRIMARY KEY (`id`)
)"""

            try:
                cursor.execute(query)
            except:
                pass

            query = """CREATE TABLE `emailMarketing_validationlog` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `status` int(11) NOT NULL,
  `message` longtext NOT NULL,
  `owner_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `emailMarketing_valid_owner_id_240ad36e_fk_emailMark` (`owner_id`),
  CONSTRAINT `emailMarketing_valid_owner_id_240ad36e_fk_emailMark` FOREIGN KEY (`owner_id`) REFERENCES `emailMarketing_emaillists` (`id`)
)"""

            try:
                cursor.execute(query)
            except:
                pass

            try:
                connection.close()
            except:
                pass
        except:
            pass

    @staticmethod
    def dockerMigrations():
        try:
            connection, cursor = Upgrade.setupConnection('cyberpanel')

            query = """CREATE TABLE `dockerManager_containers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `cid` varchar(64) NOT NULL,
  `image` varchar(50) NOT NULL,
  `tag` varchar(50) NOT NULL,
  `memory` int(11) NOT NULL,
  `ports` longtext NOT NULL,
  `env` longtext NOT NULL,
  `startOnReboot` int(11) NOT NULL,
  `admin_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `dockerManager_contai_admin_id_58fb62b7_fk_loginSyst` (`admin_id`),
  CONSTRAINT `dockerManager_contai_admin_id_58fb62b7_fk_loginSyst` FOREIGN KEY (`admin_id`) REFERENCES `loginSystem_administrator` (`id`)
)"""
            try:
                cursor.execute(query)
            except:
                pass

            try:
                cursor.execute('ALTER TABLE loginSystem_administrator ADD config longtext')
            except:
                pass

            try:
                cursor.execute('ALTER TABLE loginSystem_acl ADD config longtext')
            except:
                pass

            try:
                cursor.execute('ALTER TABLE dockerManager_containers ADD volumes longtext')
            except:
                pass

            try:
                cursor.execute('ALTER TABLE dockerManager_containers MODIFY COLUMN name VARCHAR(150);')
            except:
                pass

            try:
                connection.close()
            except:
                pass
        except:
            pass

    @staticmethod
    def containerMigrations():
        try:
            connection, cursor = Upgrade.setupConnection('cyberpanel')

            query = """CREATE TABLE `containerization_containerlimits` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cpuPers` varchar(10) NOT NULL,
  `IO` varchar(10) NOT NULL,
  `IOPS` varchar(10) NOT NULL,
  `memory` varchar(10) NOT NULL,
  `networkSpeed` varchar(10) NOT NULL,
  `networkHexValue` varchar(10) NOT NULL,
  `enforce` int(11) NOT NULL,
  `owner_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `containerization_con_owner_id_494eb637_fk_websiteFu` (`owner_id`),
  CONSTRAINT `containerization_con_owner_id_494eb637_fk_websiteFu` FOREIGN KEY (`owner_id`) REFERENCES `websiteFunctions_websites` (`id`)
)"""
            try:
                cursor.execute(query)
            except:
                pass

            query = """CREATE TABLE `websiteFunctions_dockerpackages` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `Name` varchar(100) NOT NULL, `CPUs` integer NOT NULL, `Ram` integer NOT NULL, `Bandwidth` longtext NOT NULL, `DiskSpace` longtext NOT NULL, `config` longtext NOT NULL);"""
            try:
                cursor.execute(query)
            except:
                pass

            query = """CREATE TABLE `websiteFunctions_dockersites` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `ComposePath` longtext NOT NULL, `SitePath` longtext NOT NULL, `MySQLPath` longtext NOT NULL, `state` integer NOT NULL, `SiteType` integer NOT NULL, `MySQLDBName` varchar(100) NOT NULL, `MySQLDBNUser` varchar(100) NOT NULL, `CPUsMySQL` varchar(100) NOT NULL, `MemoryMySQL` varchar(100) NOT NULL, `port` varchar(100) NOT NULL, `CPUsSite` varchar(100) NOT NULL, `MemorySite` varchar(100) NOT NULL, `SiteName` varchar(255) NOT NULL UNIQUE, `finalURL` longtext NOT NULL, `blogTitle` longtext NOT NULL, `adminUser` varchar(100) NOT NULL, `adminEmail` varchar(100) NOT NULL, `admin_id` integer NOT NULL);"""
            try:
                cursor.execute(query)
            except:
                pass

            query = "ALTER TABLE `websiteFunctions_dockersites` ADD CONSTRAINT `websiteFunctions_doc_admin_id_88f5cb6d_fk_websiteFu` FOREIGN KEY (`admin_id`) REFERENCES `websiteFunctions_websites` (`id`);"
            try:
                cursor.execute(query)
            except:
                pass

            query = "CREATE TABLE `websiteFunctions_packageassignment` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `package_id` integer NOT NULL, `user_id` integer NOT NULL);"
            try:
                cursor.execute(query)
            except:
                pass


            query = """ALTER TABLE `websiteFunctions_packageassignment` ADD CONSTRAINT `websiteFunctions_pac_package_id_420b6aff_fk_websiteFu` FOREIGN KEY (`package_id`) REFERENCES `websiteFunctions_dockerpackages` (`id`);"""
            try:
                cursor.execute(query)
            except:
                pass

            query = "ALTER TABLE `websiteFunctions_packageassignment` ADD CONSTRAINT `websiteFunctions_pac_user_id_864958ce_fk_loginSyst` FOREIGN KEY (`user_id`) REFERENCES `loginSystem_administrator` (`id`);"
            try:
                cursor.execute(query)
            except:
                pass

            query = """ALTER TABLE `websiteFunctions_dockersites` ADD CONSTRAINT `websiteFunctions_doc_admin_id_88f5cb6d_fk_websiteFu` FOREIGN KEY (`admin_id`) REFERENCES `websiteFunctions_websites` (`id`);"""
            try:
                cursor.execute(query)
            except:
                pass

            try:
                connection.close()
            except:
                pass
        except:
            pass

    @staticmethod
    def CLMigrations():
        try:
            connection, cursor = Upgrade.setupConnection('cyberpanel')

            query = """CREATE TABLE `CLManager_clpackages` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `speed` varchar(50) NOT NULL,
  `vmem` varchar(50) NOT NULL,
  `pmem` varchar(50) NOT NULL,
  `io` varchar(50) NOT NULL,
  `iops` varchar(50) NOT NULL,
  `ep` varchar(50) NOT NULL,
  `nproc` varchar(50) NOT NULL,
  `inodessoft` varchar(50) NOT NULL,
  `inodeshard` varchar(50) NOT NULL,
  `owner_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `CLManager_clpackages_owner_id_9898c1e8_fk_packages_package_id` (`owner_id`),
  CONSTRAINT `CLManager_clpackages_owner_id_9898c1e8_fk_packages_package_id` FOREIGN KEY (`owner_id`) REFERENCES `packages_package` (`id`)
)"""
            try:
                cursor.execute(query)
            except:
                pass

            query = "ALTER TABLE packages_package ADD COLUMN allowFullDomain INT DEFAULT 1;"
            try:
                cursor.execute(query)
            except:
                pass

            query = "ALTER TABLE packages_package ADD COLUMN enforceDiskLimits INT DEFAULT 0;"
            try:
                cursor.execute(query)
            except:
                pass

            try:
                connection.close()
            except:
                pass
        except:
            pass

    @staticmethod
    def manageServiceMigrations():
        try:
            connection, cursor = Upgrade.setupConnection('cyberpanel')

            query = """CREATE TABLE `manageServices_pdnsstatus` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `serverStatus` int(11) NOT NULL,
  `type` varchar(6) NOT NULL,
  PRIMARY KEY (`id`)
)"""
            try:
                cursor.execute(query)
            except:
                pass

            try:
                cursor.execute('alter table manageServices_pdnsstatus add masterServer varchar(200)')
            except:
                pass

            try:
                cursor.execute('alter table manageServices_pdnsstatus add masterIP varchar(200)')
            except:
                pass

            try:
                cursor.execute('ALTER TABLE `manageServices_pdnsstatus` CHANGE `type` `type` VARCHAR(10) NULL;')
            except:
                pass

            query = '''CREATE TABLE `databases_dbmeta` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `key` varchar(200) NOT NULL,
  `value` longtext NOT NULL,
  `database_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `databases_dbmeta_database_id_777997bc_fk_databases_databases_id` (`database_id`),
  CONSTRAINT `databases_dbmeta_database_id_777997bc_fk_databases_databases_id` FOREIGN KEY (`database_id`) REFERENCES `databases_databases` (`id`)
)'''

            try:
                cursor.execute(query)
            except:
                pass

            query = """CREATE TABLE `filemanager_trash` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `originalPath` varchar(500) NOT NULL,
  `fileName` varchar(200) NOT NULL,
  `website_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `filemanager_trash_website_id_e2762f3c_fk_websiteFu` (`website_id`),
  CONSTRAINT `filemanager_trash_website_id_e2762f3c_fk_websiteFu` FOREIGN KEY (`website_id`) REFERENCES `websiteFunctions_websites` (`id`)
)"""

            try:
                cursor.execute(query)
            except:
                pass

            query = """CREATE TABLE `databases_globaluserdb` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(200) NOT NULL,
  `password` varchar(500) NOT NULL,
  `token` varchar(20) NOT NULL,
  PRIMARY KEY (`id`)
)"""

            try:
                cursor.execute(query)
            except:
                pass

            query = "CREATE TABLE `databases_databasesusers` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `username` varchar(50) NOT NULL UNIQUE, `owner_id` integer NOT NULL)"

            try:
                cursor.execute(query)
            except:
                pass

            query = "ALTER TABLE `databases_databasesusers` ADD CONSTRAINT `databases_databasesu_owner_id_908fc638_fk_databases` FOREIGN KEY (`owner_id`) REFERENCES `databases_databases` (`id`);"

            try:
                cursor.execute(query)
            except:
                pass

            try:
                connection.close()
            except:
                pass
        except:
            pass

    @staticmethod
    def GeneralMigrations():
        try:

            cwd = os.getcwd()
            os.chdir('/usr/local/CyberCP')

            command = '/usr/local/CyberPanel/bin/python manage.py makemigrations'
            Upgrade.executioner(command, 'python manage.py makemigrations', 0)

            command = '/usr/local/CyberPanel/bin/python manage.py makemigrations'
            Upgrade.executioner(command, '/usr/local/CyberPanel/bin/python manage.py migrate', 0)

            os.chdir(cwd)

        except:
            pass

    @staticmethod
    def IncBackupMigrations():
        try:
            connection, cursor = Upgrade.setupConnection('cyberpanel')

            query = """CREATE TABLE `IncBackups_backupjob` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `destination` varchar(300) NOT NULL,
  `frequency` varchar(50) NOT NULL,
  `websiteData` int(11) NOT NULL,
  `websiteDatabases` int(11) NOT NULL,
  `websiteDataEmails` int(11) NOT NULL,
  PRIMARY KEY (`id`)
)"""
            try:
                cursor.execute(query)
            except:
                pass

            query = 'ALTER TABLE IncBackups_backupjob ADD retention integer DEFAULT 0'

            try:
                cursor.execute(query)
            except:
                pass

            query = """CREATE TABLE `IncBackups_incjob` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` datetime(6) NOT NULL,
  `website_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `IncBackups_incjob_website_id_aad31bf6_fk_websiteFu` (`website_id`),
  CONSTRAINT `IncBackups_incjob_website_id_aad31bf6_fk_websiteFu` FOREIGN KEY (`website_id`) REFERENCES `websiteFunctions_websites` (`id`)
)"""
            try:
                cursor.execute(query)
            except:
                pass

            query = """CREATE TABLE `IncBackups_jobsites` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `website` varchar(300) NOT NULL,
  `job_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `IncBackups_jobsites_job_id_494a1f69_fk_IncBackups_backupjob_id` (`job_id`),
  CONSTRAINT `IncBackups_jobsites_job_id_494a1f69_fk_IncBackups_backupjob_id` FOREIGN KEY (`job_id`) REFERENCES `IncBackups_backupjob` (`id`)
)"""
            try:
                cursor.execute(query)
            except:
                pass

            query = """CREATE TABLE `IncBackups_jobsnapshots` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` varchar(300) NOT NULL,
  `snapshotid` varchar(50) NOT NULL,
  `job_id` int(11) NOT NULL,
  `destination` varchar(200) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `IncBackups_jobsnapshots_job_id_a8237ca8_fk_IncBackups_incjob_id` (`job_id`),
  CONSTRAINT `IncBackups_jobsnapshots_job_id_a8237ca8_fk_IncBackups_incjob_id` FOREIGN KEY (`job_id`) REFERENCES `IncBackups_incjob` (`id`)
)"""
            try:
                cursor.execute(query)
            except:
                pass

            query = """CREATE TABLE `websiteFunctions_gitlogs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` datetime(6) NOT NULL,
  `type` varchar(5) NOT NULL,
  `message` longtext NOT NULL,
  `owner_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `websiteFunctions_git_owner_id_ce74c7de_fk_websiteFu` (`owner_id`),
  CONSTRAINT `websiteFunctions_git_owner_id_ce74c7de_fk_websiteFu` FOREIGN KEY (`owner_id`) REFERENCES `websiteFunctions_websites` (`id`)
)"""

            try:
                cursor.execute(query)
            except:
                pass

            query = """CREATE TABLE `websiteFunctions_backupjob` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `logFile` varchar(1000) NOT NULL,
  `ipAddress` varchar(50) NOT NULL,
  `port` varchar(15) NOT NULL,
  `jobFailedSites` int(11) NOT NULL,
  `jobSuccessSites` int(11) NOT NULL,
  `location` int(11) NOT NULL,
  PRIMARY KEY (`id`)
)"""
            try:
                cursor.execute(query)
            except:
                pass

            query = """CREATE TABLE `websiteFunctions_backupjoblogs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `message` longtext NOT NULL,
  `owner_id` int(11) NOT NULL,
  `status` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `websiteFunctions_bac_owner_id_af3d15f9_fk_websiteFu` (`owner_id`),
  CONSTRAINT `websiteFunctions_bac_owner_id_af3d15f9_fk_websiteFu` FOREIGN KEY (`owner_id`) REFERENCES `websiteFunctions_backupjob` (`id`)
)"""

            try:
                cursor.execute(query)
            except:
                pass

            query = """CREATE TABLE `websiteFunctions_gdrive` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `auth` longtext NOT NULL,
  `runTime` varchar(20) NOT NULL,
  `owner_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `websiteFunctions_gdr_owner_id_b5b1e86f_fk_loginSyst` (`owner_id`),
  CONSTRAINT `websiteFunctions_gdr_owner_id_b5b1e86f_fk_loginSyst` FOREIGN KEY (`owner_id`) REFERENCES `loginSystem_administrator` (`id`)
)"""

            try:
                cursor.execute(query)
            except:
                pass

            query = """CREATE TABLE `websiteFunctions_gdrivesites` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `domain` varchar(200) NOT NULL,
  `owner_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `websiteFunctions_gdr_owner_id_ff78b305_fk_websiteFu` (`owner_id`),
  CONSTRAINT `websiteFunctions_gdr_owner_id_ff78b305_fk_websiteFu` FOREIGN KEY (`owner_id`) REFERENCES `websiteFunctions_gdrive` (`id`)
)"""

            try:
                cursor.execute(query)
            except:
                pass

            query = """CREATE TABLE `websiteFunctions_gdrivejoblogs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `status` int(11) NOT NULL,
  `message` longtext NOT NULL,
  `owner_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `websiteFunctions_gdr_owner_id_4cf7983e_fk_websiteFu` (`owner_id`),
  CONSTRAINT `websiteFunctions_gdr_owner_id_4cf7983e_fk_websiteFu` FOREIGN KEY (`owner_id`) REFERENCES `websiteFunctions_gdrive` (`id`)
)"""

            try:
                cursor.execute(query)
            except:
                pass

            query = "ALTER TABLE `websiteFunctions_childdomains` ADD `alais` INT NOT NULL DEFAULT '0' AFTER `master_id`; "
            try:
                cursor.execute(query)
            except:
                pass


            try:
                connection.close()
            except:
                pass
        except:
            pass

    @staticmethod
    def enableServices():
        try:
            servicePath = '/home/cyberpanel/powerdns'
            writeToFile = open(servicePath, 'w+')
            writeToFile.close()

            servicePath = '/home/cyberpanel/postfix'
            writeToFile = open(servicePath, 'w+')
            writeToFile.close()

            servicePath = '/home/cyberpanel/pureftpd'
            writeToFile = open(servicePath, 'w+')
            writeToFile.close()
        except:
            pass

    @staticmethod
    def downloadAndUpgrade(versionNumbring, branch):
        try:
            ## Download latest version.

            ## Backup settings file.

            Upgrade.stdOut("Backing up settings file.")

            ## CyberPanel DB Creds
            dbName = settings.DATABASES['default']['NAME']
            dbUser = settings.DATABASES['default']['USER']
            password = settings.DATABASES['default']['PASSWORD']
            host = settings.DATABASES['default']['HOST']
            port = settings.DATABASES['default']['PORT']

            ## Root DB Creds

            rootdbName = settings.DATABASES['rootdb']['NAME']
            rootdbdbUser = settings.DATABASES['rootdb']['USER']
            rootdbpassword = settings.DATABASES['rootdb']['PASSWORD']

            ## Complete db string

            completDBString = """\nDATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '%s',
        'USER': '%s',
        'PASSWORD': '%s',
        'HOST': '%s',
        'PORT':'%s'
    },
    'rootdb': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '%s',
        'USER': '%s',
        'PASSWORD': '%s',
        'HOST': '%s',
        'PORT': '%s',
    },
}\n""" % (dbName, dbUser, password, host, port, rootdbName, rootdbdbUser, rootdbpassword, host, port)

            settingsFile = '/usr/local/CyberCP/CyberCP/settings.py'

            Upgrade.stdOut("Settings file backed up.")

            ## Check git branch status

            os.chdir('/usr/local/CyberCP')

            command = 'git config --global user.email "support@cyberpanel.net"'

            if not Upgrade.executioner(command, command, 1):
                return 0, 'Failed to execute %s' % (command)

            command = 'git config --global user.name "CyberPanel"'

            if not Upgrade.executioner(command, command, 1):
                return 0, 'Failed to execute %s' % (command)

            command = 'git status'
            currentBranch = subprocess.check_output(shlex.split(command)).decode()

            if currentBranch.find('On branch %s' % (branch)) > -1 and currentBranch.find(
                    'On branch %s-dev' % (branch)) == -1:

                command = 'git stash'
                if not Upgrade.executioner(command, command, 1):
                    return 0, 'Failed to execute %s' % (command)

                command = 'git pull'
                if not Upgrade.executioner(command, command, 1):
                    return 0, 'Failed to execute %s' % (command)

            elif currentBranch.find('not a git repository') > -1:

                os.chdir('/usr/local')

                command = 'git clone https://github.com/quantum-host/webpanel'
                if not Upgrade.executioner(command, command, 1):
                    return 0, 'Failed to execute %s' % (command)

                if os.path.exists('CyberCP'):
                    shutil.rmtree('CyberCP')

                shutil.move('cyberpanel', 'CyberCP')

            else:

                command = 'git fetch'
                if not Upgrade.executioner(command, command, 1):
                    return 0, 'Failed to execute %s' % (command)

                command = 'git stash'
                if not Upgrade.executioner(command, command, 1):
                    return 0, 'Failed to execute %s' % (command)

                command = 'git checkout %s' % (branch)
                if not Upgrade.executioner(command, command, 1):
                    return 0, 'Failed to execute %s' % (command)

                command = 'git pull'
                if not Upgrade.executioner(command, command, 1):
                    return 0, 'Failed to execute %s' % (command)

            ## Copy settings file

            settingsData = open(settingsFile, 'r').readlines()

            DATABASESCHECK = 0
            writeToFile = open(settingsFile, 'w')

            for items in settingsData:
                if items.find('DATABASES = {') > -1:
                    DATABASESCHECK = 1

                if DATABASESCHECK == 0:
                    writeToFile.write(items)

                if items.find('DATABASE_ROUTERS = [') > -1:
                    DATABASESCHECK = 0
                    writeToFile.write(completDBString)
                    writeToFile.write(items)

            writeToFile.close()

            Upgrade.stdOut('Settings file restored!')

            Upgrade.staticContent()

            return 1, None

        except BaseException as msg:
            return 0, str(msg)

    @staticmethod
    def installLSCPD(branch):
        try:

            if Upgrade.SoftUpgrade == 0:

                Upgrade.stdOut("Starting LSCPD installation..")

                cwd = os.getcwd()

                os.chdir('/usr/local')

                command = 'yum -y install gcc gcc-c++ make autoconf glibc rcs'
                Upgrade.executioner(command, 'LSCPD Pre-reqs [one]', 0)

                ##

                lscpdPath = '/usr/local/lscp/bin/lscpd'

                if os.path.exists(lscpdPath):
                    os.remove(lscpdPath)

                try:
                    try:
                        result = subprocess.run('uname -a', capture_output=True, universal_newlines=True, shell=True)
                    except:
                        result = subprocess.run('uname -a', stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)

                    if result.stdout.find('aarch64') == -1:
                        lscpdSelection = 'lscpd-0.3.1'
                        if os.path.exists(Upgrade.UbuntuPath):
                            result = open(Upgrade.UbuntuPath, 'r').read()
                            if result.find('22.04') > -1:
                                lscpdSelection = 'lscpd.0.4.0'
                    else:
                        lscpdSelection = 'lscpd.aarch64'

                except:

                    lscpdSelection = 'lscpd-0.3.1'
                    if os.path.exists(Upgrade.UbuntuPath):
                        result = open(Upgrade.UbuntuPath, 'r').read()
                        if result.find('22.04') > -1:
                            lscpdSelection = 'lscpd.0.4.0'

                command = f'cp -f /usr/local/CyberCP/{lscpdSelection} /usr/local/lscp/bin/{lscpdSelection}'
                Upgrade.executioner(command, command, 0)

                command = 'rm -f /usr/local/lscp/bin/lscpd'
                Upgrade.executioner(command, command, 0)

                command = f'mv /usr/local/lscp/bin/{lscpdSelection} /usr/local/lscp/bin/lscpd'
                Upgrade.executioner(command, command, 0)

                command = f'chmod 755 {lscpdPath}'
                Upgrade.executioner(command, 'LSCPD Download.', 0)

                command = 'yum -y install pcre-devel openssl-devel expat-devel geoip-devel zlib-devel udns-devel which curl'
                Upgrade.executioner(command, 'LSCPD Pre-reqs [two]', 0)

                try:
                    pwd.getpwnam('lscpd')
                except KeyError:
                    command = 'adduser lscpd -M -d /usr/local/lscp'
                    Upgrade.executioner(command, 'Add user LSCPD', 0)

                try:
                    grp.getgrnam('lscpd')
                except KeyError:
                    command = 'groupadd lscpd'
                    Upgrade.executioner(command, 'Add group LSCPD', 0)

                command = 'usermod -a -G lscpd lscpd'
                Upgrade.executioner(command, 'Add group LSCPD', 0)

                command = 'usermod -a -G lsadm lscpd'
                Upgrade.executioner(command, 'Add group LSCPD', 0)

                command = 'systemctl daemon-reload'
                Upgrade.executioner(command, 'daemon-reload LSCPD', 0)

                command = 'systemctl restart lscpd'
                Upgrade.executioner(command, 'Restart LSCPD', 0)

                os.chdir(cwd)

                Upgrade.stdOut("LSCPD successfully installed!")

        except BaseException as msg:
            Upgrade.stdOut(str(msg) + " [installLSCPD]")

    ### disable dkim signing in rspamd in ref to https://github.com/quantum-host/webpanel/issues/1176
    @staticmethod
    def FixRSPAMDConfig():
        RSPAMDConf = '/etc/rspamd'
        postfixConf = '/etc/postfix/main.cf'

        if os.path.exists(RSPAMDConf):
            DKIMPath = '/etc/rspamd/local.d/dkim_signing.conf'

            WriteToFile = open(DKIMPath, 'w')
            WriteToFile.write('enabled = false;\n')
            WriteToFile.close()

            if os.path.exists(postfixConf):
                appendpath = "/etc/postfix/main.cf"

                lines = open(appendpath, 'r').readlines()

                WriteToFile = open(appendpath, 'w')

                for line in lines:

                    if line.find('smtpd_milters') > -1:
                        continue
                    elif line.find('non_smtpd_milters') > -1:
                        continue
                    elif line.find('milter_default_action') > -1:
                        continue
                    else:
                        WriteToFile.write(line)

                RSPAMDConfContent = '''
### Please do not edit this line, editing this line could break configurations
smtpd_milters = inet:127.0.0.1:8891, inet:127.0.0.1:11332
non_smtpd_milters = $smtpd_milters
milter_default_action = accept
'''
                WriteToFile.write(RSPAMDConfContent)

                WriteToFile.close()

                command = 'systemctl restart postfix && systemctl restart rspamd'
                Upgrade.executioner(command, 'postfix and rspamd restart', 0, True)

    #### if you update this function needs to update this function on plogical.acl.py as well
    @staticmethod
    def fixPermissions():
        try:

            try:
                def generate_pass(length=14):
                    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
                    size = length
                    return ''.join(random.choice(chars) for x in range(size))

                content = """<?php
$_ENV['snappymail_INCLUDE_AS_API'] = true;
include '/usr/local/CyberCP/public/snappymail/index.php';

$oConfig = \snappymail\Api::Config();
$oConfig->SetPassword('%s');
echo $oConfig->Save() ? 'Done' : 'Error';

?>""" % (generate_pass())

                writeToFile = open('/usr/local/CyberCP/public/snappymail.php', 'w')
                writeToFile.write(content)
                writeToFile.close()

                command = "chown -R lscpd:lscpd /usr/local/lscp/cyberpanel/snappymail/data"
                subprocess.call(shlex.split(command))

            except:
                pass

            Upgrade.stdOut("Fixing permissions..")

            command = "usermod -G lscpd,lsadm,nobody lscpd"
            Upgrade.executioner(command, 'chown core code', 0)

            command = "usermod -G lscpd,lsadm,nogroup lscpd"
            Upgrade.executioner(command, 'chown core code', 0)

            ###### fix Core CyberPanel permissions

            command = "find /usr/local/CyberCP -type d -exec chmod 0755 {} \;"
            Upgrade.executioner(command, 'chown core code', 0)

            command = "find /usr/local/CyberCP -type f -exec chmod 0644 {} \;"
            Upgrade.executioner(command, 'chown core code', 0)

            command = "chmod -R 755 /usr/local/CyberCP/bin"
            Upgrade.executioner(command, 'chown core code', 0)

            ## change owner

            command = "chown -R root:root /usr/local/CyberCP"
            Upgrade.executioner(command, 'chown core code', 0)

            ########### Fix LSCPD

            command = "find /usr/local/lscp -type d -exec chmod 0755 {} \;"
            Upgrade.executioner(command, 'chown core code', 0)

            command = "find /usr/local/lscp -type f -exec chmod 0644 {} \;"
            Upgrade.executioner(command, 'chown core code', 0)

            command = "chmod -R 755 /usr/local/lscp/bin"
            Upgrade.executioner(command, 'chown core code', 0)

            command = "chmod -R 755 /usr/local/lscp/fcgi-bin"
            Upgrade.executioner(command, 'chown core code', 0)

            command = "chown -R lscpd:lscpd /usr/local/CyberCP/public/phpmyadmin/tmp"
            Upgrade.executioner(command, 'chown core code', 0)

            ## change owner

            command = "chown -R root:root /usr/local/lscp"
            Upgrade.executioner(command, 'chown core code', 0)

            command = "chown -R lscpd:lscpd /usr/local/lscp/cyberpanel/rainloop"
            Upgrade.executioner(command, 'chown core code', 0)

            command = "chmod 700 /usr/local/CyberCP/cli/cyberPanel.py"
            Upgrade.executioner(command, 'chown core code', 0)

            command = "chmod 700 /usr/local/CyberCP/plogical/upgradeCritical.py"
            Upgrade.executioner(command, 'chown core code', 0)

            command = "chmod 755 /usr/local/CyberCP/postfixSenderPolicy/client.py"
            Upgrade.executioner(command, 'chown core code', 0)

            command = "chmod 640 /usr/local/CyberCP/CyberCP/settings.py"
            Upgrade.executioner(command, 'chown core code', 0)

            command = "chown root:cyberpanel /usr/local/CyberCP/CyberCP/settings.py"
            Upgrade.executioner(command, 'chown core code', 0)

            command = 'chmod +x /usr/local/CyberCP/CLManager/CLPackages.py'
            Upgrade.executioner(command, 'chmod CLPackages', 0)

            files = ['/etc/yum.repos.d/MariaDB.repo', '/etc/pdns/pdns.conf', '/etc/systemd/system/lscpd.service',
                     '/etc/pure-ftpd/pure-ftpd.conf', '/etc/pure-ftpd/pureftpd-pgsql.conf',
                     '/etc/pure-ftpd/pureftpd-mysql.conf', '/etc/pure-ftpd/pureftpd-ldap.conf',
                     '/etc/dovecot/dovecot.conf', '/usr/local/lsws/conf/httpd_config.xml',
                     '/usr/local/lsws/conf/modsec.conf', '/usr/local/lsws/conf/httpd.conf']

            for items in files:
                command = 'chmod 644 %s' % (items)
                Upgrade.executioner(command, 'chown core code', 0)

            impFile = ['/etc/pure-ftpd/pure-ftpd.conf', '/etc/pure-ftpd/pureftpd-pgsql.conf',
                       '/etc/pure-ftpd/pureftpd-mysql.conf', '/etc/pure-ftpd/pureftpd-ldap.conf',
                       '/etc/dovecot/dovecot.conf', '/etc/pdns/pdns.conf', '/etc/pure-ftpd/db/mysql.conf',
                       '/etc/powerdns/pdns.conf']

            for items in impFile:
                command = 'chmod 600 %s' % (items)
                Upgrade.executioner(command, 'chown core code', 0)

            command = 'chmod 640 /etc/postfix/*.cf'
            subprocess.call(command, shell=True)

            command = 'chmod 640 /etc/dovecot/*.conf'
            subprocess.call(command, shell=True)

            command = 'chmod 640 /etc/dovecot/dovecot-sql.conf.ext'
            subprocess.call(command, shell=True)

            fileM = ['/usr/local/lsws/FileManager/', '/usr/local/CyberCP/install/FileManager',
                     '/usr/local/CyberCP/serverStatus/litespeed/FileManager',
                     '/usr/local/lsws/Example/html/FileManager']

            for items in fileM:
                try:
                    shutil.rmtree(items)
                except:
                    pass

            command = 'chmod 755 /etc/pure-ftpd/'
            subprocess.call(command, shell=True)

            command = 'chmod 644 /etc/dovecot/dovecot.conf'
            subprocess.call(command, shell=True)

            command = 'chmod 644 /etc/postfix/main.cf'
            subprocess.call(command, shell=True)

            command = 'chmod 644 /etc/postfix/dynamicmaps.cf'
            subprocess.call(command, shell=True)

            command = 'chmod +x /usr/local/CyberCP/plogical/renew.py'
            Upgrade.executioner(command, command, 0)

            command = 'chmod +x /usr/local/CyberCP/CLManager/CLPackages.py'
            Upgrade.executioner(command, command, 0)

            clScripts = ['/usr/local/CyberCP/CLScript/panel_info.py',
                         '/usr/local/CyberCP/CLScript/CloudLinuxPackages.py',
                         '/usr/local/CyberCP/CLScript/CloudLinuxUsers.py',
                         '/usr/local/CyberCP/CLScript/CloudLinuxDomains.py'
                , '/usr/local/CyberCP/CLScript/CloudLinuxResellers.py',
                         '/usr/local/CyberCP/CLScript/CloudLinuxAdmins.py',
                         '/usr/local/CyberCP/CLScript/CloudLinuxDB.py', '/usr/local/CyberCP/CLScript/UserInfo.py']

            for items in clScripts:
                command = 'chmod +x %s' % (items)
                Upgrade.executioner(command, 0)

            command = 'chmod 600 /usr/local/CyberCP/plogical/adminPass.py'
            Upgrade.executioner(command, 0)

            command = 'chmod 600 /etc/cagefs/exclude/cyberpanelexclude'
            Upgrade.executioner(command, 0)

            command = "find /usr/local/CyberCP/ -name '*.pyc' -delete"
            Upgrade.executioner(command, 0)

            if os.path.exists(Upgrade.CentOSPath) or os.path.exists(Upgrade.openEulerPath):
                command = 'chown root:pdns /etc/pdns/pdns.conf'
                Upgrade.executioner(command, 0)

                command = 'chmod 640 /etc/pdns/pdns.conf'
                Upgrade.executioner(command, 0)
            else:
                command = 'chown root:pdns /etc/powerdns/pdns.conf'
                Upgrade.executioner(command, 0)

                command = 'chmod 640 /etc/powerdns/pdns.conf'
                Upgrade.executioner(command, 0)

            command = 'chmod 640 /usr/local/lscp/cyberpanel/logs/access.log'
            Upgrade.executioner(command, 0)

            command = '/usr/local/lsws/lsphp72/bin/php /usr/local/CyberCP/public/snappymail.php'
            Upgrade.executioner(command, 0)

            command = 'chmod 600 /usr/local/CyberCP/public/snappymail.php'
            Upgrade.executioner(command, 0)

            ###

            WriteToFile = open('/etc/fstab', 'a')
            WriteToFile.write('proc    /proc        proc        defaults,hidepid=2    0 0\n')
            WriteToFile.close()

            command = 'mount -o remount,rw,hidepid=2 /proc'
            Upgrade.executioner(command, 0)

            ###

            CentOSPath = '/etc/redhat-release'
            openEulerPath = '/etc/openEuler-release'

            if not os.path.exists(CentOSPath) or not os.path.exists(openEulerPath):
                group = 'nobody'
            else:
                group = 'nogroup'

            command = 'chown root:%s /usr/local/lsws/logs' % (group)
            Upgrade.executioner(command, 0)

            command = 'chmod 750 /usr/local/lsws/logs'
            Upgrade.executioner(command, 0)

            ## symlink protection

            writeToFile = open('/usr/lib/sysctl.d/50-default.conf', 'a')
            writeToFile.writelines('fs.protected_hardlinks = 1\n')
            writeToFile.writelines('fs.protected_symlinks = 1\n')
            writeToFile.close()

            command = 'sysctl --system'
            Upgrade.executioner(command, 0)

            command = 'chmod 700 %s' % ('/home/cyberpanel')
            Upgrade.executioner(command, 0)

            destPrivKey = "/usr/local/lscp/conf/key.pem"

            command = 'chmod 600 %s' % (destPrivKey)
            Upgrade.executioner(command, 0)

            Upgrade.stdOut("Permissions updated.")

        except BaseException as msg:
            Upgrade.stdOut(str(msg) + " [fixPermissions]")

    @staticmethod
    def AutoUpgradeAcme():
        command = '/root/.acme.sh/acme.sh --upgrade --auto-upgrade'
        Upgrade.executioner(command, command, 0)
        command = '/root/.acme.sh/acme.sh --set-default-ca  --server  letsencrypt'
        Upgrade.executioner(command, command, 0)

    @staticmethod
    def installPHP73():
        try:
            if Upgrade.installedOutput.find('lsphp73') == -1:
                command = 'yum install -y lsphp73 lsphp73-json lsphp73-xmlrpc lsphp73-xml lsphp73-tidy lsphp73-soap lsphp73-snmp ' \
                          'lsphp73-recode lsphp73-pspell lsphp73-process lsphp73-pgsql lsphp73-pear lsphp73-pdo lsphp73-opcache ' \
                          'lsphp73-odbc lsphp73-mysqlnd lsphp73-mcrypt lsphp73-mbstring lsphp73-ldap lsphp73-intl lsphp73-imap ' \
                          'lsphp73-gmp lsphp73-gd lsphp73-enchant lsphp73-dba  lsphp73-common  lsphp73-bcmath'
                Upgrade.executioner(command, 'Install PHP 73, 0')

            if Upgrade.installedOutput.find('lsphp74') == -1:
                command = 'yum install -y lsphp74 lsphp74-json lsphp74-xmlrpc lsphp74-xml lsphp74-tidy lsphp74-soap lsphp74-snmp ' \
                          'lsphp74-recode lsphp74-pspell lsphp74-process lsphp74-pgsql lsphp74-pear lsphp74-pdo lsphp74-opcache ' \
                          'lsphp74-odbc lsphp74-mysqlnd lsphp74-mcrypt lsphp74-mbstring lsphp74-ldap lsphp74-intl lsphp74-imap ' \
                          'lsphp74-gmp lsphp74-gd lsphp74-enchant lsphp74-dba lsphp74-common  lsphp74-bcmath'

                Upgrade.executioner(command, 'Install PHP 74, 0')

            if Upgrade.installedOutput.find('lsphp80') == -1:
                command = 'yum install lsphp80* -y'
                subprocess.call(command, shell=True)

            if Upgrade.installedOutput.find('lsphp81') == -1:
                command = 'yum install lsphp81* -y'
                subprocess.call(command, shell=True)

            if Upgrade.installedOutput.find('lsphp82') == -1:
                command = 'yum install lsphp82* -y'
                subprocess.call(command, shell=True)

            command = 'yum install lsphp83* -y'
            subprocess.call(command, shell=True)

        except:
            command = 'DEBIAN_FRONTEND=noninteractive apt-get -y install ' \
                      'lsphp7? lsphp7?-common lsphp7?-curl lsphp7?-dev lsphp7?-imap lsphp7?-intl lsphp7?-json ' \
                      'lsphp7?-ldap lsphp7?-mysql lsphp7?-opcache lsphp7?-pspell lsphp7?-recode ' \
                      'lsphp7?-sqlite3 lsphp7?-tidy'
            Upgrade.executioner(command, 'Install PHP 73, 0')

            command = 'DEBIAN_FRONTEND=noninteractive apt-get -y install lsphp80*'
            os.system(command)

            command = 'DEBIAN_FRONTEND=noninteractive apt-get -y install lsphp81*'
            os.system(command)

            command = 'DEBIAN_FRONTEND=noninteractive apt-get -y install lsphp82*'
            os.system(command)

            command = 'DEBIAN_FRONTEND=noninteractive apt-get -y install lsphp83*'
            os.system(command)

        CentOSPath = '/etc/redhat-release'
        openEulerPath = '/etc/openEuler-release'

        # if not os.path.exists(CentOSPath) or not os.path.exists(openEulerPath):
        # command = 'cp /usr/local/lsws/lsphp71/bin/php /usr/bin/'
        # Upgrade.executioner(command, 'Set default PHP 7.0, 0')

    @staticmethod
    def someDirectories():
        command = "mkdir -p /usr/local/lscpd/admin/"
        Upgrade.executioner(command, 0)

        command = "mkdir -p /usr/local/lscp/cyberpanel/logs"
        Upgrade.executioner(command, 0)

    @staticmethod
    def upgradeDovecot():
        try:
            Upgrade.stdOut("Upgrading Dovecot..")
            CentOSPath = '/etc/redhat-release'
            openEulerPath = '/etc/openEuler-release'

            dovecotConfPath = '/etc/dovecot/'
            postfixConfPath = '/etc/postfix/'

            ## Take backup of configurations

            configbackups = '/home/cyberpanel/configbackups'

            command = 'mkdir %s' % (configbackups)
            Upgrade.executioner(command, 0)

            command = 'cp -pR %s %s' % (dovecotConfPath, configbackups)
            Upgrade.executioner(command, 0)

            command = 'cp -pR %s %s' % (postfixConfPath, configbackups)
            Upgrade.executioner(command, 0)

            if Upgrade.FindOperatingSytem() == CENTOS8 or Upgrade.FindOperatingSytem() == CENTOS7 or Upgrade.FindOperatingSytem() == openEuler22 or Upgrade.FindOperatingSytem() == openEuler20:

                command = "yum makecache -y"
                Upgrade.executioner(command, 0)

                command = "yum update -y"
                Upgrade.executioner(command, 0)

                if Upgrade.FindOperatingSytem() == CENTOS8:
                    command = 'dnf remove dovecot23 dovecot23-mysql -y'
                    Upgrade.executioner(command, 0)

                    command = 'dnf install --enablerepo=gf-plus dovecot23 dovecot23-mysql -y'
                    Upgrade.executioner(command, 0)

                import django
                os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CyberCP.settings")
                django.setup()
                from mailServer.models import EUsers

                Upgrade.stdOut("Upgrading passwords...")
                for items in EUsers.objects.all():
                    if items.password.find('CRYPT') > -1:
                        continue
                    command = 'doveadm pw -p %s' % (items.password)
                    items.password = subprocess.check_output(shlex.split(command)).decode("utf-8").strip('\n')
                    items.save()

                command = "systemctl restart dovecot"
                Upgrade.executioner(command, 0)

                ### Postfix Upgrade

                command = 'yum remove postfix -y'
                Upgrade.executioner(command, 0)

                command = 'yum clean all'
                Upgrade.executioner(command, 0)

                if Upgrade.FindOperatingSytem() == CENTOS7:
                    command = 'yum makecache fast'
                else:
                    command = 'yum makecache -y'

                Upgrade.executioner(command, 0)

                if Upgrade.FindOperatingSytem() == CENTOS7:
                    command = 'yum install --enablerepo=gf-plus -y postfix3 postfix3-ldap postfix3-mysql postfix3-pcre'
                else:
                    command = 'dnf install --enablerepo=gf-plus postfix3 postfix3-mysql -y'

                Upgrade.executioner(command, 0)

                ### Restore dovecot/postfix conf

                command = 'cp -pR %s/dovecot/ /etc/' % (configbackups)
                Upgrade.executioner(command, 0)

                command = 'cp -pR %s/postfix/ /etc/' % (configbackups)
                Upgrade.executioner(command, 0)

                ## Restored

                command = 'systemctl restart postfix'
                Upgrade.executioner(command, 0)
            elif Upgrade.FindOperatingSytem() == Ubuntu20 or Upgrade.FindOperatingSytem() == Ubuntu22:

                debPath = '/etc/apt/sources.list.d/dovecot.list'
                # writeToFile = open(debPath, 'w')
                # writeToFile.write('deb https://repo.dovecot.org/ce-2.3-latest/ubuntu/focal focal main\n')
                # writeToFile.close()
                #
                # command = "apt update -y"
                # Upgrade.executioner(command, command)
                #
                # command = 'dpkg --configure -a'
                # subprocess.call(command, shell=True)
                #
                # command = 'apt --fix-broken install -y'
                # subprocess.call(command, shell=True)
                #
                # command = 'DEBIAN_FRONTEND=noninteractive DEBIAN_PRIORITY=critical apt -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" upgrade -y'
                # subprocess.call(command, shell=True)

            dovecotConf = '/etc/dovecot/dovecot.conf'

            dovecotContent = open(dovecotConf, 'r').read()

            if dovecotContent.find('service stats') == -1:
                writeToFile = open(dovecotConf, 'a')

                content = """\nservice stats {
    unix_listener stats-reader {
        user = vmail
        group = vmail
        mode = 0660
    }
    unix_listener stats-writer {
        user = vmail
        group = vmail
        mode = 0660
    }
}\n"""

                writeToFile.write(content)
                writeToFile.close()

                command = 'systemctl restart dovecot'
                Upgrade.executioner(command, command, 0)

                command = 'rm -rf %s' % (configbackups)
                Upgrade.executioner(command, command, 0)

            Upgrade.stdOut("Dovecot upgraded.")

        except BaseException as msg:
            Upgrade.stdOut(str(msg) + " [upgradeDovecot]")

    @staticmethod
    def installRestic():
        CentOSPath = '/etc/redhat-release'
        openEulerPath = '/etc/openEuler-release'

        if os.path.exists(CentOSPath) or os.path.exists(openEulerPath):
            if Upgrade.installedOutput.find('restic') == -1:
                command = 'yum install restic -y'
                Upgrade.executioner(command, 'Install Restic')
                command = 'restic self-update'
                Upgrade.executioner(command, 'Install Restic')
        else:

            if Upgrade.installedOutput.find('restic/bionic,now 0.8') == -1:
                command = 'apt-get update -y'
                Upgrade.executioner(command, 'Install Restic')

                command = 'apt-get install restic -y'
                Upgrade.executioner(command, 'Install Restic')

                command = 'restic self-update'
                Upgrade.executioner(command, 'Install Restic')

    @staticmethod
    def UpdateMaxSSLCons():
        command = "sed -i 's|<maxConnections>2000</maxConnections>|<maxConnections>10000</maxConnections>|g' /usr/local/lsws/conf/httpd_config.xml"
        Upgrade.executioner(command, 0)

        command = "sed -i 's|<maxSSLConnections>200</maxSSLConnections>|<maxSSLConnections>10000</maxSSLConnections>|g' /usr/local/lsws/conf/httpd_config.xml"
        Upgrade.executioner(command, 0)

    @staticmethod
    def installCLScripts():
        try:

            CentOSPath = '/etc/redhat-release'
            openEulerPath = '/etc/openEuler-release'

            if os.path.exists(CentOSPath) or os.path.exists(openEulerPath):
                command = 'mkdir -p /opt/cpvendor/etc/'
                Upgrade.executioner(command, 0)

                content = """[integration_scripts]

panel_info = /usr/local/CyberCP/CLScript/panel_info.py
packages = /usr/local/CyberCP/CLScript/CloudLinuxPackages.py
users = /usr/local/CyberCP/CLScript/CloudLinuxUsers.py
domains = /usr/local/CyberCP/CLScript/CloudLinuxDomains.py
resellers = /usr/local/CyberCP/CLScript/CloudLinuxResellers.py
admins = /usr/local/CyberCP/CLScript/CloudLinuxAdmins.py
db_info = /usr/local/CyberCP/CLScript/CloudLinuxDB.py

[lvemanager_config]
ui_user_info = /usr/local/CyberCP/CLScript/UserInfo.py
base_path = /usr/local/lvemanager
run_service = 1
service_port = 9000
"""

                if not os.path.exists('/opt/cpvendor/etc/integration.ini'):
                    writeToFile = open('/opt/cpvendor/etc/integration.ini', 'w')
                    writeToFile.write(content)
                    writeToFile.close()

                command = 'mkdir -p /etc/cagefs/exclude'
                Upgrade.executioner(command, command, 0)

                content = """cyberpanel
docker
ftpuser
lscpd
opendkim
pdns
vmail
"""

                writeToFile = open('/etc/cagefs/exclude/cyberpanelexclude', 'w')
                writeToFile.write(content)
                writeToFile.close()

        except:
            pass

    @staticmethod
    def runSomeImportantBash():

        # Remove invalid crons from /etc/crontab Reference: https://github.com/quantum-host/webpanel/issues/216
        command = """sed -i '/CyberCP/d' /etc/crontab"""
        Upgrade.executioner(command, command, 0, True)

        if os.path.exists('/usr/local/lsws/conf/httpd.conf'):
            # Setup /usr/local/lsws/conf/httpd.conf to use new Logformat standard for better stats and accesslogs
            command = """sed -i "s|^LogFormat.*|LogFormat '%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"' combined|g" /usr/local/lsws/conf/httpd.conf"""
            Upgrade.executioner(command, command, 0, True)

        # Fix all existing vhost confs to use new Logformat standard for better stats and accesslogs
        command = """find /usr/local/lsws/conf/vhosts/ -type f -name 'vhost.conf' -exec sed -i "s/.*CustomLog.*/    LogFormat '%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"' combined\n&/g" {} \;"""
        Upgrade.executioner(command, command, 0, True)

        # Install any Cyberpanel missing crons to root crontab so its visible to users via crontab -l as root user

        # Install findBWUsage cron if missing

        CentOSPath = '/etc/redhat-release'
        openEulerPath = '/etc/openEuler-release'

        if os.path.exists(CentOSPath) or os.path.exists(openEulerPath):
            cronPath = '/var/spool/cron/root'
        else:
            cronPath = '/var/spool/cron/crontabs/root'

        if os.path.exists(cronPath):
            data = open(cronPath, 'r').read()

            if data.find('findBWUsage') == -1:
                content = """
0 * * * * /usr/local/CyberCP/bin/python /usr/local/CyberCP/plogical/findBWUsage.py >/dev/null 2>&1
0 * * * * /usr/local/CyberCP/bin/python /usr/local/CyberCP/postfixSenderPolicy/client.py hourlyCleanup >/dev/null 2>&1
0 0 1 * * /usr/local/CyberCP/bin/python /usr/local/CyberCP/postfixSenderPolicy/client.py monthlyCleanup >/dev/null 2>&1
0 2 * * * /usr/local/CyberCP/bin/python /usr/local/CyberCP/plogical/upgradeCritical.py >/dev/null 2>&1
0 0 * * 4 /usr/local/CyberCP/bin/python /usr/local/CyberCP/plogical/renew.py >/dev/null 2>&1
7 0 * * * "/root/.acme.sh"/acme.sh --cron --home "/root/.acme.sh" > /dev/null
*/3 * * * * if ! find /home/*/public_html/ -maxdepth 2 -type f -newer /usr/local/lsws/cgid -name '.htaccess' -exec false {} +; then /usr/local/lsws/bin/lswsctrl restart; fi
"""

                writeToFile = open(cronPath, 'w')
                writeToFile.write(content)
                writeToFile.close()

            if data.find('IncScheduler.py') == -1:
                content = """
0 12 * * * /usr/local/CyberCP/bin/python /usr/local/CyberCP/IncBackups/IncScheduler.py Daily
0 0 * * 0 /usr/local/CyberCP/bin/python /usr/local/CyberCP/IncBackups/IncScheduler.py Weekly
"""
                writeToFile = open(cronPath, 'a')
                writeToFile.write(content)
                writeToFile.close()

            if data.find("IncScheduler.py '30 Minutes'") == -1:
                content = """
*/30 * * * * /usr/local/CyberCP/bin/python /usr/local/CyberCP/IncBackups/IncScheduler.py '30 Minutes'
0 * * * * /usr/local/CyberCP/bin/python /usr/local/CyberCP/IncBackups/IncScheduler.py '1 Hour'
0 */6 * * * /usr/local/CyberCP/bin/python /usr/local/CyberCP/IncBackups/IncScheduler.py '6 Hours'
0 */12 * * * /usr/local/CyberCP/bin/python /usr/local/CyberCP/IncBackups/IncScheduler.py '12 Hours'
0 1 * * * /usr/local/CyberCP/bin/python /usr/local/CyberCP/IncBackups/IncScheduler.py '1 Day'
0 0 */3 * * /usr/local/CyberCP/bin/python /usr/local/CyberCP/IncBackups/IncScheduler.py '3 Days'
0 0 * * 0 /usr/local/CyberCP/bin/python /usr/local/CyberCP/IncBackups/IncScheduler.py '1 Week'
"""
                writeToFile = open(cronPath, 'a')
                writeToFile.write(content)
                writeToFile.close()


        else:
            content = """
0 * * * * /usr/local/CyberCP/bin/python /usr/local/CyberCP/plogical/findBWUsage.py >/dev/null 2>&1
0 * * * * /usr/local/CyberCP/bin/python /usr/local/CyberCP/postfixSenderPolicy/client.py hourlyCleanup >/dev/null 2>&1
0 0 1 * * /usr/local/CyberCP/bin/python /usr/local/CyberCP/postfixSenderPolicy/client.py monthlyCleanup >/dev/null 2>&1
0 2 * * * /usr/local/CyberCP/bin/python /usr/local/CyberCP/plogical/upgradeCritical.py >/dev/null 2>&1
0 0 * * 4 /usr/local/CyberCP/bin/python /usr/local/CyberCP/plogical/renew.py >/dev/null 2>&1
7 0 * * * "/root/.acme.sh"/acme.sh --cron --home "/root/.acme.sh" > /dev/null
0 0 * * * /usr/local/CyberCP/bin/python /usr/local/CyberCP/IncBackups/IncScheduler.py Daily
0 0 * * 0 /usr/local/CyberCP/bin/python /usr/local/CyberCP/IncBackups/IncScheduler.py Weekly
"""
            writeToFile = open(cronPath, 'w')
            writeToFile.write(content)
            writeToFile.close()

        ### Check and remove OLS restart if lsws ent detected

        if not os.path.exists('/usr/local/lsws/bin/openlitespeed'):

            data = open(cronPath, 'r').readlines()

            writeToFile = open(cronPath, 'w')

            for items in data:
                if items.find('-maxdepth 2 -type f -newer') > -1:
                    pass
                else:
                    writeToFile.writelines(items)

            writeToFile.close()

        if not os.path.exists(CentOSPath) or not os.path.exists(openEulerPath):
            command = 'chmod 600 %s' % (cronPath)
            Upgrade.executioner(command, 0)

    @staticmethod
    def UpdateConfigOfCustomACL():
        sys.path.append('/usr/local/CyberCP')
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CyberCP.settings")
        import django
        django.setup()
        from loginSystem.models import ACL
        for acl in ACL.objects.all():
            if acl.name == 'admin' or acl.name == 'reseller' or acl.name == 'user':
                continue
            elif acl.config == '{}':
                acl.config = '{"adminStatus":%s, "versionManagement": %s, "createNewUser": %s, "listUsers": %s, "deleteUser": %s, "resellerCenter": %s, "changeUserACL": %s, "createWebsite": %s, "modifyWebsite": %s, "suspendWebsite": %s, "deleteWebsite": %s, "createPackage": %s, "listPackages": %s, "deletePackage": %s, "modifyPackage": %s, "createDatabase": %s, "deleteDatabase": %s, "listDatabases": %s, "createNameServer": %s, "createDNSZone": %s, "deleteZone": %s, "addDeleteRecords": %s, "createEmail": %s, "listEmails": %s, "deleteEmail": %s, "emailForwarding": %s, "changeEmailPassword": %s, "dkimManager": %s, "createFTPAccount": %s, "deleteFTPAccount": %s, "listFTPAccounts": %s, "createBackup": %s, "restoreBackup": %s, "addDeleteDestinations": %s, "scheduleBackups": %s, "remoteBackups": %s, "googleDriveBackups": %s, "manageSSL": %s, "hostnameSSL": %s, "mailServerSSL": %s }' \
                             % (str(acl.adminStatus), str(acl.versionManagement), str(acl.createNewUser),
                                str(acl.listUsers), str(acl.deleteUser), str(acl.resellerCenter),
                                str(acl.changeUserACL),
                                str(acl.createWebsite), str(acl.modifyWebsite), str(acl.suspendWebsite),
                                str(acl.deleteWebsite),
                                str(acl.createPackage), str(acl.listPackages), str(acl.deletePackage),
                                str(acl.modifyPackage),
                                str(acl.createDatabase), str(acl.deleteDatabase), str(acl.listDatabases),
                                str(acl.createNameServer),
                                str(acl.createDNSZone), str(acl.deleteZone), str(acl.addDeleteRecords),
                                str(acl.createEmail),
                                str(acl.listEmails), str(acl.deleteEmail), str(acl.emailForwarding),
                                str(acl.changeEmailPassword),
                                str(acl.dkimManager), str(acl.createFTPAccount), str(acl.deleteFTPAccount),
                                str(acl.listFTPAccounts),
                                str(acl.createBackup), str(acl.restoreBackup), str(acl.addDeleteDestinations),
                                str(acl.scheduleBackups), str(acl.remoteBackups), '1',
                                str(acl.manageSSL), str(acl.hostnameSSL), str(acl.mailServerSSL))
                acl.save()

    @staticmethod
    def CreateMissingPoolsforFPM():
        ##### apache configs

        CentOSPath = '/etc/redhat-release'

        if os.path.exists(CentOSPath):

            serverRootPath = '/etc/httpd'
            configBasePath = '/etc/httpd/conf.d/'
            php54Path = '/opt/remi/php54/root/etc/php-fpm.d/'
            php55Path = '/opt/remi/php55/root/etc/php-fpm.d/'
            php56Path = '/etc/opt/remi/php56/php-fpm.d/'
            php70Path = '/etc/opt/remi/php70/php-fpm.d/'
            php71Path = '/etc/opt/remi/php71/php-fpm.d/'
            php72Path = '/etc/opt/remi/php72/php-fpm.d/'
            php73Path = '/etc/opt/remi/php73/php-fpm.d/'

            php74Path = '/etc/opt/remi/php74/php-fpm.d/'

            php80Path = '/etc/opt/remi/php80/php-fpm.d/'
            php81Path = '/etc/opt/remi/php81/php-fpm.d/'
            php82Path = '/etc/opt/remi/php82/php-fpm.d/'

            php83Path = '/etc/opt/remi/php83/php-fpm.d/'
            php84Path = '/etc/opt/remi/php84/php-fpm.d/'
            php85Path = '/etc/opt/remi/php85/php-fpm.d/'

            serviceName = 'httpd'
            sockPath = '/var/run/php-fpm/'
            runAsUser = 'apache'
        else:
            serverRootPath = '/etc/apache2'
            configBasePath = '/etc/apache2/sites-enabled/'

            php54Path = '/etc/php/5.4/fpm/pool.d/'
            php55Path = '/etc/php/5.5/fpm/pool.d/'
            php56Path = '/etc/php/5.6/fpm/pool.d/'
            php70Path = '/etc/php/7.0/fpm/pool.d/'
            php71Path = '/etc/php/7.1/fpm/pool.d/'
            php72Path = '/etc/php/7.2/fpm/pool.d/'
            php73Path = '/etc/php/7.3/fpm/pool.d/'

            php74Path = '/etc/php/7.4/fpm/pool.d/'
            php80Path = '/etc/php/8.0/fpm/pool.d/'
            php81Path = '/etc/php/8.1/fpm/pool.d/'
            php82Path = '/etc/php/8.2/fpm/pool.d/'
            php83Path = '/etc/php/8.3/fpm/pool.d/'
            php84Path = '/etc/php/8.4/fpm/pool.d/'
            php85Path = '/etc/php/8.5/fpm/pool.d/'

            serviceName = 'apache2'
            sockPath = '/var/run/php/'
            runAsUser = 'www-data'

        #####

        if not os.path.exists(serverRootPath):
            return 1

        if os.path.exists(php54Path):
            content = f"""
[php54default]
user = {runAsUser}
group = {runAsUser}
listen ={sockPath}php5.4-fpm.sock
listen.owner = {runAsUser}
listen.group = {runAsUser}
pm = dynamic
pm.max_children = 5
pm.start_servers = 2
pm.min_spare_servers = 1
pm.max_spare_servers = 3
"""
            WriteToFile = open(f'{php54Path}www.conf', 'w')
            WriteToFile.write(content)
            WriteToFile.close()

        if os.path.exists(php55Path):
            content = f'''
[php55default]
user = {runAsUser}
group = {runAsUser}
listen ={sockPath}php5.5-fpm.sock
listen.owner = {runAsUser}
listen.group = {runAsUser}
pm = dynamic
pm.max_children = 5
pm.start_servers = 2
pm.min_spare_servers = 1
pm.max_spare_servers = 3
'''
            WriteToFile = open(f'{php55Path}www.conf', 'w')
            WriteToFile.write(content)
            WriteToFile.close()

        if os.path.exists(php56Path):
            content = f'''
[php56default]
user = {runAsUser}
group = {runAsUser}
listen ={sockPath}php5.6-fpm.sock
listen.owner = {runAsUser}
listen.group = {runAsUser}
pm = dynamic
pm.max_children = 5
pm.start_servers = 2
pm.min_spare_servers = 1
pm.max_spare_servers = 3
'''
            WriteToFile = open(f'{php56Path}www.conf', 'w')
            WriteToFile.write(content)
            WriteToFile.close()

        if os.path.exists(php70Path):
            content = f'''
[php70default]
user = {runAsUser}
group = {runAsUser}
listen ={sockPath}php7.0-fpm.sock
listen.owner = {runAsUser}
listen.group = {runAsUser}
pm = dynamic
pm.max_children = 5
pm.start_servers = 2
pm.min_spare_servers = 1
pm.max_spare_servers = 3
'''
            WriteToFile = open(f'{php70Path}www.conf', 'w')
            WriteToFile.write(content)
            WriteToFile.close()

        if os.path.exists(php71Path):
            content = f'''
[php71default]
user = {runAsUser}
group = {runAsUser}
listen ={sockPath}php7.1-fpm.sock
listen.owner = {runAsUser}
listen.group = {runAsUser}
pm = dynamic
pm.max_children = 5
pm.start_servers = 2
pm.min_spare_servers = 1
pm.max_spare_servers = 3
'''
            WriteToFile = open(f'{php71Path}www.conf', 'w')
            WriteToFile.write(content)
            WriteToFile.close()

        if os.path.exists(php72Path):
            content = f'''
[php72default]
user = {runAsUser}
group = {runAsUser}
listen ={sockPath}php7.2-fpm.sock
listen.owner = {runAsUser}
listen.group = {runAsUser}
pm = dynamic
pm.max_children = 5
pm.start_servers = 2
pm.min_spare_servers = 1
pm.max_spare_servers = 3
'''
            WriteToFile = open(f'{php72Path}www.conf', 'w')
            WriteToFile.write(content)
            WriteToFile.close()

        if os.path.exists(php73Path):
            content = f'''
[php73default]
user = {runAsUser}
group = {runAsUser}
listen ={sockPath}php7.3-fpm.sock
listen.owner = {runAsUser}
listen.group = {runAsUser}
pm = dynamic
pm.max_children = 5
pm.start_servers = 2
pm.min_spare_servers = 1
pm.max_spare_servers = 3
'''
            WriteToFile = open(f'{php73Path}www.conf', 'w')
            WriteToFile.write(content)
            WriteToFile.close()

        if os.path.exists(php74Path):
            content = f'''
[php74default]
user = {runAsUser}
group = {runAsUser}
listen ={sockPath}php7.4-fpm.sock
listen.owner = {runAsUser}
listen.group = {runAsUser}
pm = dynamic
pm.max_children = 5
pm.start_servers = 2
pm.min_spare_servers = 1
pm.max_spare_servers = 3
'''
            WriteToFile = open(f'{php74Path}www.conf', 'w')
            WriteToFile.write(content)
            WriteToFile.close()

        if os.path.exists(php80Path):
            content = f'''
[php80default]
user = {runAsUser}
group = {runAsUser}
listen ={sockPath}php8.0-fpm.sock
listen.owner = {runAsUser}
listen.group = {runAsUser}
pm = dynamic
pm.max_children = 5
pm.start_servers = 2
pm.min_spare_servers = 1
pm.max_spare_servers = 3

'''
            WriteToFile = open(f'{php80Path}www.conf', 'w')
            WriteToFile.write(content)
            WriteToFile.close()

        if os.path.exists(php81Path):
            content = f'''
[php81default]
user = {runAsUser}
group = {runAsUser}
listen ={sockPath}php8.1-fpm.sock
listen.owner = {runAsUser}
listen.group = {runAsUser}
pm = dynamic
pm.max_children = 5
pm.start_servers = 2
pm.min_spare_servers = 1
pm.max_spare_servers = 3

'''
            WriteToFile = open(f'{php81Path}www.conf', 'w')
            WriteToFile.write(content)
            WriteToFile.close()
        if os.path.exists(php82Path):
            content = f'''
[php82default]
user = {runAsUser}
group = {runAsUser}
listen ={sockPath}php8.2-fpm.sock
listen.owner = {runAsUser}
listen.group = {runAsUser}
pm = dynamic
pm.max_children = 5
pm.start_servers = 2
pm.min_spare_servers = 1
pm.max_spare_servers = 3
            
'''
            WriteToFile = open(f'{php82Path}www.conf', 'w')
            WriteToFile.write(content)
            WriteToFile.close()

        if os.path.exists(php83Path):
            content = f'''
[php83default]
user = {runAsUser}
group = {runAsUser}
listen ={sockPath}php8.3-fpm.sock
listen.owner = {runAsUser}
listen.group = {runAsUser}
pm = dynamic
pm.max_children = 5
pm.start_servers = 2
pm.min_spare_servers = 1
pm.max_spare_servers = 3
'''
            WriteToFile = open(f'{php83Path}www.conf', 'w')
            WriteToFile.write(content)
            WriteToFile.close()

        if os.path.exists(php84Path):
            content = f'''
[php84default]
user = {runAsUser}
group = {runAsUser}
listen ={sockPath}php8.4-fpm.sock
listen.owner = {runAsUser}
listen.group = {runAsUser}
pm = dynamic
pm.max_children = 5
pm.start_servers = 2
pm.min_spare_servers = 1
pm.max_spare_servers = 3
'''
            WriteToFile = open(f'{php84Path}www.conf', 'w')
            WriteToFile.write(content)
            WriteToFile.close()

        if os.path.exists(php85Path):
            content = f'''
[php85default]
user = {runAsUser}
group = {runAsUser}
listen ={sockPath}php8.5-fpm.sock
listen.owner = {runAsUser}
listen.group = {runAsUser}
pm = dynamic
pm.max_children = 5
pm.start_servers = 2
pm.min_spare_servers = 1
pm.max_spare_servers = 3
'''
            WriteToFile = open(f'{php85Path}www.conf', 'w')
            WriteToFile.write(content)
            WriteToFile.close()

    @staticmethod
    def upgrade(branch):

        if branch.find('SoftUpgrade') > -1:
            Upgrade.SoftUpgrade = 1
            branch = branch.split(',')[1]

        # Upgrade.stdOut("Upgrades are currently disabled")
        # return 0

        if os.path.exists(Upgrade.CentOSPath) or os.path.exists(Upgrade.openEulerPath):
            command = 'yum list installed'
            Upgrade.installedOutput = subprocess.check_output(shlex.split(command)).decode()
        else:
            command = 'apt list'
            Upgrade.installedOutput = subprocess.check_output(shlex.split(command)).decode()

        # command = 'systemctl stop cpssh'
        # Upgrade.executioner(command, 'fix csf if there', 0)

        ## Add LSPHP7.4 TO LSWS Ent configs

        if not os.path.exists('/usr/local/lsws/bin/openlitespeed'):

            if os.path.exists('httpd_config.xml'):
                os.remove('httpd_config.xml')

            command = 'wget https://raw.githubusercontent.com/quantum-host/webpanel/stable/install/litespeed/httpd_config.xml'
            Upgrade.executioner(command, command, 0)
            # os.remove('/usr/local/lsws/conf/httpd_config.xml')
            # shutil.copy('httpd_config.xml', '/usr/local/lsws/conf/httpd_config.xml')

        Upgrade.updateRepoURL()

        os.chdir("/usr/local")

        if os.path.exists(Upgrade.CentOSPath) or os.path.exists(Upgrade.openEulerPath):
            command = 'yum remove yum-plugin-priorities -y'
            Upgrade.executioner(command, 'remove yum-plugin-priorities', 0)

        ## Current Version

        ### if this is a soft upgrade from front end do not stop lscpd, as lscpd is controlling the front end

        if Upgrade.SoftUpgrade == 0:
            command = "systemctl stop lscpd"
            Upgrade.executioner(command, 'stop lscpd', 0)

        Upgrade.fixSudoers()
        # Upgrade.mountTemp()

        ### fix a temp issue causing upgrade problem

        fstab = "/etc/fstab"

        if open(fstab, 'r').read().find('/usr/.tempdisk')>-1:
            command = 'umount -l /tmp'
            Upgrade.executioner(command, 'tmp adjustment', 0)

            command = 'mount -t tmpfs -o size=2G tmpfs /tmp'
            Upgrade.executioner(command, 'tmp adjustment', 0)

        Upgrade.dockerUsers()
        Upgrade.setupComposer()

        ##

        versionNumbring = Upgrade.downloadLink()

        if os.path.exists('/usr/local/CyberPanel.' + versionNumbring):
            os.remove('/usr/local/CyberPanel.' + versionNumbring)

        ##

        # execPath = "sudo /usr/local/CyberCP/bin/python /usr/local/CyberCP/plogical/csf.py"
        # execPath = execPath + " removeCSF"
        # Upgrade.executioner(execPath, 'fix csf if there', 0)

        Upgrade.downloadAndUpgrade(versionNumbring, branch)
        versionNumbring = Upgrade.downloadLink()
        Upgrade.download_install_phpmyadmin()
        Upgrade.downoad_and_install_raindloop()

        ##

        ##

        Upgrade.mailServerMigrations()
        Upgrade.emailMarketingMigrationsa()
        Upgrade.dockerMigrations()
        Upgrade.CLMigrations()
        Upgrade.IncBackupMigrations()
        Upgrade.installRestic()

        ##

        # Upgrade.setupVirtualEnv()

        ##

        Upgrade.applyLoginSystemMigrations()

        ## Put function here to update custom ACLs

        Upgrade.UpdateConfigOfCustomACL()

        Upgrade.s3BackupMigrations()
        Upgrade.containerMigrations()
        Upgrade.manageServiceMigrations()
        Upgrade.enableServices()

        Upgrade.installPHP73()
        Upgrade.setupCLI()
        Upgrade.someDirectories()
        Upgrade.installLSCPD(branch)
        Upgrade.FixCurrentQuoatasSystem()

        ### General migrations are not needed any more

        # Upgrade.GeneralMigrations()

        # Upgrade.p3()

        ## Also disable email service upgrade

        # if os.path.exists(postfixPath):
        #     Upgrade.upgradeDovecot()

        ## Upgrade version

        Upgrade.fixPermissions()

        ##

        ### Disable version upgrade too

        # Upgrade.upgradeVersion()

        Upgrade.UpdateMaxSSLCons()

        ## Update LSCPD PHP

        phpPath = '/usr/local/lscp/fcgi-bin/lsphp'

        try:
            os.remove(phpPath)
        except:
            pass

        command = 'cp /usr/local/lsws/lsphp80/bin/lsphp %s' % (phpPath)
        Upgrade.executioner(command, 0)

        if Upgrade.SoftUpgrade == 0:
            try:
                command = "systemctl start lscpd"
                Upgrade.executioner(command, 'Start LSCPD', 0)
            except:
                pass

        #command = 'csf -uf'
        #Upgrade.executioner(command, 'fix csf if there', 0)

        if os.path.exists('/etc/csf'):
            ##### Function to backup custom csf files and restore

            from datetime import datetime

            # List of files to backup
            FILES = [
                "/etc/csf/csf.allow",
                "/etc/csf/csf.deny",
                "/etc/csf/csf.conf",
                "/etc/csf/csf.ignore",
                "/etc/csf/csf.rignore",
                "/etc/csf/csf.blocklists",
                "/etc/csf/csf.dyndns"
            ]

            # Directory for backups
            BACKUP_DIR = f"/home/cyberpanel/csf_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Backup function
            def backup_files():
                os.makedirs(BACKUP_DIR, exist_ok=True)
                for file in FILES:
                    if os.path.exists(file):
                        shutil.copy(file, BACKUP_DIR)
                        print(f"Backed up: {file}")
                    else:
                        print(f"File not found, skipping: {file}")

            # Restore function
            def restore_files():
                for file in FILES:
                    backup_file = os.path.join(BACKUP_DIR, os.path.basename(file))
                    if os.path.exists(backup_file):
                        try:
                            shutil.copy(backup_file, file)
                            print(f"Restored: {file}")
                        except:
                            pass
                    else:
                        print(f"Backup not found for: {file}")

            # Backup the files
            print("Backing up files...")
            backup_files()

            execPath = "sudo /usr/local/CyberCP/bin/python /usr/local/CyberCP/plogical/csf.py"
            execPath = execPath + " removeCSF"
            Upgrade.executioner(execPath, 'fix csf if there', 0)

            execPath = "sudo /usr/local/CyberCP/bin/python /usr/local/CyberCP/plogical/csf.py"
            execPath = execPath + " installCSF"

            # Restore the files
            print("Restoring files...")
            restore_files()


            Upgrade.executioner(execPath, 'fix csf if there', 0)



        # if os.path.exists('/usr/local/CyberCP/configservercsf'):
        #     command = 'rm -f /usr/local/CyberCP/configservercsf/signals.py'
        #     Upgrade.executioner(command, 'remove /usr/local/CyberCP/configservercsf/signals.py', 1)
        #
        #
        # sed_commands = [
        #     'sed -i "s/url(r\'^configservercsf/path(\'configservercsf/g" /usr/local/CyberCP/CyberCP/urls.py',
        #     'sed -i "s/from django.conf.urls import url/from django.urls import path/g" /usr/local/CyberCP/configservercsf/urls.py',
        #     'sed -i "s/import signals/import configservercsf.signals/g" /usr/local/CyberCP/configservercsf/apps.py',
        #     'sed -i "s/url(r\'^$\'/path(\'\'/g" /usr/local/CyberCP/configservercsf/urls.py',
        #     'sed -i "s|url(r\'^iframe/$\'|path(\'iframe/\'|g" /usr/local/CyberCP/configservercsf/urls.py',
        #     'sed -i -E "s/from.*, response/from plogical.httpProc import httpProc/g" /usr/local/CyberCP/configservercsf/views.py'
        #     '''sed -i -E "s#^(\s*)return render.*index\.html.*#\1proc = httpProc(request, 'configservercsf/index.html', None, 'admin')\n\1return proc.render()#g" /usr/local/CyberCP/configservercsf/views.py'''
        #     'killall lswsgi'
        # ]
        #
        # for cmd in sed_commands:
        #     Upgrade.executioner(cmd, 'fix csf if there', 1)



        command = 'systemctl stop cpssh'
        Upgrade.executioner(command, 'fix csf if there', 0)
        Upgrade.AutoUpgradeAcme()
        Upgrade.installCLScripts()
        Upgrade.runSomeImportantBash()
        Upgrade.FixRSPAMDConfig()
        Upgrade.CreateMissingPoolsforFPM()

        # ## Move static files
        #
        # imunifyPath = '/usr/local/CyberCP/public/imunify'
        #
        # if os.path.exists(imunifyPath):
        #     command = "yum reinstall imunify360-firewall-generic -y"
        #     Upgrade.executioner(command, command, 1)
        #
        imunifyAVPath = '/etc/sysconfig/imunify360/integration.conf'

        if os.path.exists(imunifyAVPath):
            execPath = "/usr/local/CyberCP/bin/python /usr/local/CyberCP/CLManager/CageFS.py"
            command = execPath + " --function submitinstallImunifyAV"
            Upgrade.executioner(command, command, 1)

            command = 'chmod +x /usr/local/CyberCP/public/imunifyav/bin/execute.py'
            Upgrade.executioner(command, command, 1)

        imfExecutePath = '/usr/local/CyberCP/public/imunify/bin/execute.py'
        if os.path.exists(imfExecutePath):
            command = f'chmod 755 {imfExecutePath}'
            Upgrade.executioner(command, command, 0)


        Upgrade.installDNS_CyberPanelACMEFile()

        Upgrade.stdOut("Upgrade Completed.")

        ### remove log file path incase its there

        if Upgrade.SoftUpgrade:
            time.sleep(30)
            if os.path.exists(Upgrade.LogPathNew):
                os.remove(Upgrade.LogPathNew)

    @staticmethod
    def installQuota():
        try:

            if Upgrade.FindOperatingSytem() == CENTOS7 or Upgrade.FindOperatingSytem() == CENTOS8\
                    or Upgrade.FindOperatingSytem() == openEuler20 or Upgrade.FindOperatingSytem() == openEuler22:
                command = "yum install quota -y"
                Upgrade.executioner(command, command, 0, True)

                if Upgrade.edit_fstab('/', '/') == 0:
                    print("Quotas will not be abled as we failed to modify fstab file.")
                    return 0


                command = 'mount -o remount /'
                try:
                    mResult = subprocess.run(command, capture_output=True, universal_newlines=True, shell=True)
                except:
                    mResult = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                            universal_newlines=True, shell=True)

                if mResult.returncode != 0:
                    fstab_path = '/etc/fstab'
                    backup_path = fstab_path + '.bak'
                    if os.path.exists(fstab_path):
                        os.remove(fstab_path)
                    shutil.copy(backup_path, fstab_path)

                    print("Re-mount failed, restoring original FSTab and existing quota setup.")
                    return 0

            ##

            if Upgrade.FindOperatingSytem() == Ubuntu22 or Upgrade.FindOperatingSytem() == Ubuntu18 \
                    or Upgrade.FindOperatingSytem() == Ubuntu20:

                print("Install Quota on Ubuntu")
                command = 'apt update -y'
                Upgrade.executioner(command, command, 0, True)

                command = 'apt install quota -y'
                Upgrade.executioner(command, command, 0, True)

                command = "find /lib/modules/ -type f -name '*quota_v*.ko*'"


                if subprocess.check_output(command,shell=True).decode("utf-8").find("quota/") == -1:
                    command = "sudo apt install linux-image-extra-virtual -y"
                    Upgrade.executioner(command, command, 0, True)

                if Upgrade.edit_fstab('/', '/') == 0:
                    print("Quotas will not be abled as we are are failed to modify fstab file.")
                    return 0

                command = 'mount -o remount /'
                try:
                    mResult = subprocess.run(command, capture_output=True, universal_newlines=True, shell=True)
                except:
                    mResult = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                             universal_newlines=True, shell=True)
                if mResult.returncode != 0:
                    fstab_path = '/etc/fstab'
                    backup_path = fstab_path + '.bak'
                    if os.path.exists(fstab_path):
                        os.remove(fstab_path)
                    shutil.copy(backup_path, fstab_path)

                    print("Re-mount failed, restoring original FSTab and existing quota setup.")
                    return 0

                command = 'quotacheck -ugm /'
                try:
                    mResult = subprocess.run(command, capture_output=True, universal_newlines=True, shell=True)
                except:
                    mResult = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                             universal_newlines=True, shell=True)
                if mResult.returncode != 0:
                    fstab_path = '/etc/fstab'
                    backup_path = fstab_path + '.bak'
                    if os.path.exists(fstab_path):
                        os.remove(fstab_path)
                    shutil.copy(backup_path, fstab_path)

                    print("Re-mount failed, restoring original FSTab and existing quota setup.")
                    return 0

                ####

                command = "find /lib/modules/ -type f -name '*quota_v*.ko*'"
                try:
                    iResult = subprocess.run(command, capture_output=True, universal_newlines=True, shell=True)
                except:
                    iResult = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                             universal_newlines=True, shell=True)
                print(repr(iResult.stdout))

                # Only if the first command works, run the rest

                if iResult.returncode == 0:
                    command = "echo '{}' | sed -n 's|/lib/modules/\\([^/]*\\)/.*|\\1|p' | sort -u".format(iResult.stdout)
                    try:
                        result = subprocess.run(command, capture_output=True, universal_newlines=True, shell=True)
                    except:
                        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                                 universal_newlines=True, shell=True)
                    fResult = result.stdout.rstrip('\n')
                    print(repr(result.stdout.rstrip('\n')))

                    command  = 'uname -r'
                    try:
                        ffResult = subprocess.run(command, capture_output=True, universal_newlines=True, shell=True)
                    except:
                        ffResult = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                                universal_newlines=True, shell=True)
                    ffResult = ffResult.stdout.rstrip('\n')

                    command = f"apt-get install linux-modules-extra-{ffResult}"
                    Upgrade.executioner(command, command, 0, True)

                ###

                    command = f'modprobe quota_v1 -S {ffResult}'
                    try:
                        mResult = subprocess.run(command, capture_output=True, universal_newlines=True, shell=True)
                    except:
                        mResult = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                                  universal_newlines=True, shell=True)
                    if mResult.returncode != 0:
                        fstab_path = '/etc/fstab'
                        backup_path = fstab_path + '.bak'
                        if os.path.exists(fstab_path):
                            os.remove(fstab_path)
                        shutil.copy(backup_path, fstab_path)

                        print("Re-mount failed, restoring original FSTab and existing quota setup.")
                        return 0

                    command = f'modprobe quota_v2 -S {ffResult}'
                    try:
                        mResult = subprocess.run(command, capture_output=True, universal_newlines=True, shell=True)
                    except:
                        mResult = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                                 universal_newlines=True, shell=True)
                    if mResult.returncode != 0:
                        fstab_path = '/etc/fstab'
                        backup_path = fstab_path + '.bak'
                        if os.path.exists(fstab_path):
                            os.remove(fstab_path)
                        shutil.copy(backup_path, fstab_path)

                        print("Re-mount failed, restoring original FSTab and existing quota setup.")
                        return 0

            command = f'quotacheck -ugm /'
            try:
                mResult = subprocess.run(command, capture_output=True, universal_newlines=True, shell=True)
            except:
                mResult = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                         universal_newlines=True, shell=True)
            if mResult.returncode != 0:
                fstab_path = '/etc/fstab'
                backup_path = fstab_path + '.bak'
                if os.path.exists(fstab_path):
                    os.remove(fstab_path)
                shutil.copy(backup_path, fstab_path)

                print("Re-mount failed, restoring original FSTab and existing quota setup.")
                return 0

            command = f'quotaon -v /'
            try:
                mResult = subprocess.run(command, capture_output=True, universal_newlines=True, shell=True)
            except:
                mResult = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                         universal_newlines=True, shell=True)
            if mResult.returncode != 0:
                fstab_path = '/etc/fstab'
                backup_path = fstab_path + '.bak'
                if os.path.exists(fstab_path):
                    os.remove(fstab_path)
                shutil.copy(backup_path, fstab_path)

                print("Re-mount failed, restoring original FSTab and existing quota setup.")
                return 0

            return 1

        except BaseException as msg:
            print("[ERROR] installQuota. " + str(msg))
            return 0

    @staticmethod
    def edit_fstab(mount_point, options_to_add):
        try:
            retValue = 1
            # Backup the original fstab file
            fstab_path = '/etc/fstab'
            backup_path = fstab_path + '.bak'

            rData = open(fstab_path, 'r').read()

            if rData.find('xfs') > -1:
                options_to_add = 'uquota'
            else:
                options_to_add = 'usrquota,grpquota'

            if not os.path.exists(backup_path):
                shutil.copy(fstab_path, backup_path)

            # Read the fstab file
            with open(fstab_path, 'r') as file:
                lines = file.readlines()

            # Modify the appropriate line
            WriteToFile = open(fstab_path, 'w')
            for i, line in enumerate(lines):

                if line.find('\t') > -1:
                    parts = line.split('\t')
                else:
                    parts = line.split(' ')

                print(parts)
                try:
                    if parts[1] == '/' and parts[3].find(options_to_add) == -1 and len(parts[3]) > 4:

                        parts[3] = f'{parts[3]},{options_to_add}'
                        tempParts = [item for item in parts if item.strip()]
                        finalString = '\t'.join(tempParts)
                        print(finalString)
                        WriteToFile.write(finalString)

                    elif parts[1] == '/':

                        for ii, p in enumerate(parts):
                            if p.find('defaults') > -1 or p.find('discard') > -1 or p.find('errors=') > -1:
                                parts[ii] = f'{parts[ii]},{options_to_add}'
                                tempParts = [item for item in parts if item.strip()]
                                finalString = '\t'.join(tempParts)
                                print(finalString)
                                WriteToFile.write(finalString)
                    else:
                        WriteToFile.write(line)
                except:
                    WriteToFile.write(line)

            WriteToFile.close()

            return retValue
        except:
            return 0


    @staticmethod
    def FixCurrentQuoatasSystem():
        fstab_path = '/etc/fstab'

        data = open(fstab_path, 'r').read()

        if data.find("usrquota,grpquota") > -1 or data.find("uquota") > -1:
            print("Quotas already enabled.")


        if Upgrade.installQuota() == 1:

            print("We will attempt to bring new Quota system to old websites.")
            from websiteFunctions.models import Websites
            for website in Websites.objects.all():

                command = 'chattr -R -i /home/%s/' % (website.domain)
                Upgrade.executioner(command, command, 0, True)

                if website.package.enforceDiskLimits:
                    spaceString = f'{website.package.diskSpace}M {website.package.diskSpace}M'
                    command = f'setquota -u {website.externalApp} {spaceString} 0 0 /'
                    Upgrade.executioner(command, command, 0, True)

        else:
            print("Quotas can not be enabled continue to use chhtr.")

    @staticmethod
    def installDNS_CyberPanelACMEFile():
        filePath = '/root/.acme.sh/dns_cyberpanel.sh'
        if os.path.exists(filePath):
            os.remove(filePath)
        shutil.copy('/usr/local/CyberCP/install/dns_cyberpanel.sh', filePath)

        command = f'chmod +x {filePath}'
        Upgrade.executioner(command, command, 0, True)



def main():
    parser = argparse.ArgumentParser(description='CyberPanel Installer')
    parser.add_argument('branch', help='Install from branch name.')

    args = parser.parse_args()

    Upgrade.upgrade(args.branch)


if __name__ == "__main__":
    main()
