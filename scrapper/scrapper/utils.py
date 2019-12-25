import re


class Util:
    @staticmethod
    def normalize_address(address):
        address = address.strip().replace('\n', ', ')
        address = re.sub(r'\s+', ' ', address)
        address = address.replace(' ,', ',')
        address = re.sub(r'\,+', ',', address)
        return address

    @staticmethod
    def normalize_phone(phone):
        phone = phone.lower().split('ext')[0].strip()
        phone = re.sub(r'[\s\-\(\)A-Za-z\.\,]+', '', phone)
        if len(phone) == 11 and phone[0] == '1':
            phone = phone[1:]
        return phone
