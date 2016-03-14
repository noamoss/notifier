from _config import basedir

CRON_FILENAME = "/etc/cron.daily/notifier_mail"

def main():
    # read the cron templete
    cron_tmpl = open("./mail_sender/cron.script.tmpl", 'r')

    # setup the right path in the cron file
    cron_content = cron_tmpl.read().replace("{{PROJECT_ROOT}}", basedir)
    cron_tmpl.close()

    # write the cron file (we need permision for this)
    cron_file = open("/etc/cron.daily/notifier_mail", 'w')
    cron_file.write(cron_content)
    cron_file.close()

    # setup the right premissions for the file
    os.chmod(CRON_FILENAME, 0o751)
    

if '__main__' == __name__:
    main()

