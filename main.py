from random import Random

items = {
    26: ['Проектор', 'A-201', 'Свободно'],
    39: ['3D-принтер', 'A-305', 'Обслуживание'],
    52: ['Осциллограф', 'B-214', 'Свободно'],
    14: ['Ноутбук', 'A-108', 'Выдано'],
    27: ['Маршрутизатор', 'B-214', 'Свободно'],
    40: ['Набор микроконтроллеров', 'A-305', 'Выдано'],
    16: ['Веб-камера', 'A-108', 'Свободно'],
    29: ['Графический планшет', 'A-201', 'Обслуживание'],
    42: ['Лазерный принтер', 'A-108', 'Свободно'],
}


def chains(keys, m=13):
    a = [[] for _ in range(m)]
    for k in keys:
        a[k % m].append(k)
    return a


class HashTable:
    def __init__(self, method, m=13):
        self.method, self.m = method, m
        self.a = [None] * m
        self.n = self.collisions = self.probes = 0

    def places(self, k):
        used = set()
        for i in range(self.m):
            if self.method == 'Линейное':
                p = (k + i) % self.m
            elif self.method == 'Квадратичное':
                p = (k + i * i) % self.m
            else:
                p = (k + i * (1 + k % (self.m - 1))) % self.m
            if p in used:
                break
            used.add(p)
            yield p

    def search(self, k):
        path = []
        for p in self.places(k):
            path.append(p)
            if self.a[p] == k:
                return p, path
            if self.a[p] is None:
                break
        return None, path

    def add(self, k):
        if self.search(k)[0] is not None:
            return False
        deleted = None
        for p in self.places(k):
            self.probes += 1
            if self.a[p] == 'DEL' and deleted is None:
                deleted = p
            elif self.a[p] is None:
                self.a[p if deleted is None else deleted] = k
                self.n += 1
                return True
            elif self.a[p] != 'DEL':
                self.collisions += 1
        if deleted is not None:
            self.a[deleted] = k
            self.n += 1
            return True
        return False

    def delete(self, k):
        p, _ = self.search(k)
        if p is None:
            return False
        self.a[p] = 'DEL'
        self.n -= 1
        return True

    def resize(self, m):
        keys = [x for x in self.a if isinstance(x, int)]
        self.__init__(self.method, m)
        for k in keys:
            self.add(k)


def experiment():
    rnd = Random(2026)
    keys = rnd.sample(range(1000, 1000000), 85)
    missing = rnd.sample(range(1000001, 2000001), 300)
    for alpha in (0.25, 0.50, 0.70, 0.85):
        sample = keys[:int(101 * alpha)]
        a = chains(sample, 101)
        good = sum(a[k % 101].index(k) + 1 for k in sample) / len(sample)
        bad = sum(len(a[k % 101]) for k in missing) / len(missing)
        print(f'{alpha:.2f} Цепочки: коллизии {sum(max(0, len(b)-1) for b in a)}, '
              f'поиск {good:.2f}/{bad:.2f}, макс. цепь {max(map(len, a))}, '
              f'пустые {sum(not b for b in a)}')
        for method in ('Линейное', 'Квадратичное', 'Двойное'):
            t = HashTable(method, 101)
            for k in sample:
                t.add(k)
            good = sum(len(t.search(k)[1]) for k in sample) / len(sample)
            bad = sum(len(t.search(k)[1]) for k in missing) / len(missing)
            print(f'{alpha:.2f} {method}: коллизии {t.collisions}, '
                  f'вставка {t.probes / len(sample):.2f}, поиск {good:.2f}/{bad:.2f}, '
                  f'макс. {max(len(t.search(k)[1]) for k in sample)}, пустые {t.a.count(None)}')


print('1–2. Исходные записи и хеш-функции')
for k, record in items.items():
    print(k, *record, 'h1 =', k % 13, 'h2 =', (7 * k + 3) % 101 % 13)
for name, f in [('Деление', lambda k: k % 13),
                ('Смешивание', lambda k: (7 * k + 3) % 101 % 13)]:
    buckets = [[] for _ in range(13)]
    for k in items:
        buckets[f(k)].append(k)
    print(name, 'коллизии:', sum(max(0, len(b) - 1) for b in buckets),
          'занято:', sum(bool(b) for b in buckets), 'пусто:', sum(not b for b in buckets))

print('\n3. Метод цепочек')
a = chains(items)
print(a)
for k in (42, 91):
    bucket = a[k % 13]
    print('Поиск', k, 'найден' if k in bucket else 'не найден',
          'сравнений:', bucket.index(k) + 1 if k in bucket else len(bucket))
items[27][1:] = ['B-310', 'Выдано']
a[195 % 13].append(195)
a[39 % 13].remove(39)
a[351 % 13].append(351)
print('После изменений:', a)

print('\n4–6. Открытая адресация')
tables = [HashTable(name) for name in ('Линейное', 'Квадратичное', 'Двойное')]
for t in tables:
    for k in items:
        t.add(k)
    print(t.method, t.a, 'коллизии:', t.collisions, 'пробы:', t.probes)

print('\n7. Поиск')
for t in tables:
    for k in (42, 91):
        print(t.method, k, t.search(k))

print('\n8. Удаление')
for t in tables:
    t.add(195)
    t.delete(39)
    print(t.method, 'поиск 195:', t.search(195))
    t.add(351)
    print(t.a)

print('\n9. Рехеширование')
for t in tables:
    if (t.n + 1) / t.m > 0.7:
        t.resize(29)
    t.add(54)
    print(t.method, 'размер:', t.m, 'заполнение:', round(t.n / t.m, 3), t.a)

print('\n10. Эксперимент')
experiment()
