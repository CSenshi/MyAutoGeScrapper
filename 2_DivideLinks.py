if __name__ == "__main__":
    arr = [open('SabaLinks.txt', 'w'),
           open('BeqaLinks.txt', 'w'),
           open('NikaLinks.txt', 'w'), ]

    with open('Links/links.txt', 'r') as f:
        links = [line.rstrip() for line in f]
        totalUsers = len(arr)
        for i in range(len(links)):
            arr[i % totalUsers].write('{}\n'.format(links[i]))
