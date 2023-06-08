import os
import sys
import re
import collections
import subprocess
import requests
from colorama import init, Fore

init(autoreset=True)

def clear_console():
    subprocess.call('cls' if os.name == 'nt' else 'clear', shell=True)

def read_file(filename):
    with open(filename) as f:
        return [line.rstrip() for line in f]

def write_file(filename, lines):
    with open(filename, "w") as f:
        f.write("\n".join(lines))

def add_domains_to_check(domains):
    new_domains = []
    for domain in domains:
        if not any(d for d in words_to_check if d.startswith('@') and domain == d[1:] or domain == d):
            new_domains.append(f"@{domain}")

    if len(new_domains) > 0:
        print(Fore.YELLOW + f"Found {len(new_domains)} new domains in mails.txt:")
        for d in new_domains:
            print(Fore.YELLOW + d)
        print(Fore.YELLOW + "Do you want to add them to words_to_check.txt? [y/n]: ")
        choice = input().lower()
        while choice not in ['y', 'n']:
            print(Fore.YELLOW + "Invalid choice, please enter 'y' to add or 'n' to skip adding domains")
            choice = input().lower()

        if choice == 'y':
            write_file("words_to_check.txt", words_to_check + new_domains)
            clear_console()

def check_spam_domains(domains):
    spam_domains = []
    for domain in domains:
        if any(d for d in spam_list if d in domain):
            spam_domains.append(domain)
    return spam_domains

if __name__ == '__main__': 
    clear_console() 
    print(Fore.GREEN + "Domain Counter by FAKEDOWNBOYS aka deprussian\nv0.3.0 EXE Edition\n")

# check if mails.txt file exists in current directory, if not print an error message and exit
if not os.path.exists("mails.txt"):
    print(Fore.RED + "File mails.txt is not found in the current directory.")
    sys.exit()

# check if words_to_check.txt file exists in current directory, if not create it
if not os.path.exists("words_to_check.txt"):
    write_file("words_to_check.txt", [])
    print(Fore.YELLOW + "File words_to_check.txt is not found in the current directory. \nThe file has been created.\n")

# read words_to_check.txt and mails.txt files
words_to_check = read_file("words_to_check.txt")
lines = read_file("mails.txt")

duplicate_count = len(lines)-len(set(lines))

if duplicate_count > 0:
    # check if there are any duplicate lines in the mails.txt file, if there are ask user if they want to remove them
    print(Fore.YELLOW + f"Found {duplicate_count} duplicated lines in mails.txt\nDelete duplicated lines? [y/n]: ")
    choice = input().lower()
    while choice not in ['y', 'n']:
        print(Fore.YELLOW + "Invalid choice, please enter 'y' to delete or 'n' to keep duplicated lines")
        choice = input().lower()

    if choice == 'y':
        # remove duplicate lines from mails.txt file
        new_lines = []
        for line in lines:
            if line.strip() and "@" in line and line not in new_lines:
                new_lines.append(line)
        write_file("mails.txt", new_lines)
        lines = new_lines

# extract domain names from mails file
domains = []
for line in lines:
    match = re.search(r'@[A-Za-z0-9._%+-]+\.[A-Za-z]{2,}', line)  # regular expression to match email addresses
    if match:
        domain = match.group()[1:]
        domains.append(domain)

domains = set(domains)

spam_list_url = "https://raw.githubusercontent.com/martenson/disposable-email-domains/master/disposable_email_blocklist.conf"
try:
    # fetch spam domain list from the internet
    spam_list = requests.get(spam_list_url).text.split("\n")
except:
    print(Fore.RED + "Cannot fetch spam domain list.")
    sys.exit()

# check for spam domains in domain names extracted from mails.txt file
spam_domains = check_spam_domains(domains)
if len(spam_domains) > 0:
    # if spam domains are found, ask user if they want to delete lines with spam domains
    print(Fore.RED + "The following spam domains were found in the email list:")
    for domain in spam_domains:
        print(Fore.RED + domain)
    choice = input(Fore.YELLOW + f"Do you want to delete lines with {len(spam_domains)} spam domains? [y/n]: ").lower()
    while choice not in ['y', 'n']:
        choice = input(Fore.YELLOW + "Invalid choice, please enter 'y' or 'n': ").lower()
    if choice == 'y':
        # remove lines with spam domains from mails.txt file
        new_lines = []
        for line in lines:
            if not any(domain in line for domain in spam_domains):
                new_lines.append(line)
        write_file("mails.txt", new_lines)
        print(Fore.GREEN + f"The lines containing {len(spam_domains)} spam domains have been deleted successfully.")
        lines = new_lines
        os.execv(sys.executable, ['python'] + sys.argv)
    else:
        print(Fore.YELLOW + f"Lines with {len(spam_domains)} spam domains are not deleted.")

# add new domains to words_to_check.txt file if they don't already exist in it
add_domains_to_check(domains)

# read words_to_check.txt file again to include any new domains added to it
words_to_check = read_file("words_to_check.txt")
# count lines in mails.txt file where any domain in words_to_check list is present
count = sum(1 for line in lines if any(word in line for word in words_to_check))
print(Fore.GREEN + f"Total lines in the current database: {count}\n")

# regular expression to extract domain names from mails.txt file
regex = r"(?:(?<=\W))(?:\w+(?:(?:\.|-)\w+)*\.\w{2,})(?:(?=\W|$))"
domains = re.findall(regex, "\n".join(lines), re.MULTILINE)
# count occurrences of each domain name in the list of domain names
mails_value = collections.Counter(domains)
# sort domains by occurrence count in descending order and print them
most_common_mails = sorted(mails_value.items(), key=lambda x: x[1], reverse=True)
for domain, count in most_common_mails:
    print(f"{domain} : {count}")

while True:
    # ask user if they want to restart the program or exit
    print(Fore.RED + "\nPress 'R' to restart, or any other key to exit")
    key = input()
    if key.upper() == 'R':
        clear_console()
        os.execv(sys.executable, ['python'] + sys.argv)
    else:
        break