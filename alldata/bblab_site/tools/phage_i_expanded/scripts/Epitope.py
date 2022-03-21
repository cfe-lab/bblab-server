

class Epitope:

    def __init__(self, epitope=None, protein=None,
    hlas=None, start=None, end=None,
    source=None, r4=None, r2=None, created_at=None, updated_at=None):
        self.epitope = epitope
        self.protein = protein
        self.hlas = hlas
        self.start = int(start)
        self.end = int(end)
        self.source = source
        self.r4 = r4
        self.r2 = r2
        self.created_at = created_at
        self.updated_at = updated_at

    def __str__(self):
        return ('\t').join([(',').join(self.epitope), self.protein, (',').join(self.hlas), str(self.start), str(self.end), self.source, (',').join(self.r4), (',').join(self.r2), self.created_at, self.updated_at])

    def __repr__(self):
        return ('\t').join([(',').join(self.epitope), self.protein, (',').join(self.hlas), str(self.start), str(self.end), self.source, (',').join(self.r4), (',').join(self.r2), self.created_at, self.updated_at])

    @staticmethod
    def parseEpitopes(efile, header=True):
        results = []
        with open(efile, 'r') as f:
            if header:
                f.readline()
            for line in f:
                line = Epitope(*line.strip().split('\t'))
                line.epitope = line.epitope.split(',')
                line.hlas = line.hlas.split(',')
                line.r4 = line.r4.split(',')
                line.r2 = line.r2.split(',')
                results.append(line)
        return results

    def getPos(self, pos):
        if self.start <= pos <= self.end:
            val = str(pos - self.start + 1)
            if pos == self.end:
                val += '(C)'
        elif pos < self.start:
            val = 'N-{}'.format(self.start - pos)
        else:
            val = 'C+{}'.format(pos - self.end)
        return val