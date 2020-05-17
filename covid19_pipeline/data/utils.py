import random
from PIL import Image

def pil_loader(path):
    # open path as file to avoid ResourceWarning (https://github.com/python-pillow/Pillow/issues/835)
    with open(path, 'rb') as f:
        img = Image.open(f)
        return img.convert('RGB')

class Resampler(object):
    def __init__(self):
        pass

    @classmethod
    def resample(self, slices, threshold):
        '''
        Args:
            slices: the list of slices that requires upsampling.
            threshold: the expected number of slices
        '''
        if threshold >= len(slices):
            return self.upsample(slices, threshold)
        else:
            return self.undersample(slices, threshold)

    @staticmethod
    def upsample(slices, threshold=64):
        raise NotImplementedError

    @staticmethod
    def undersample(slices, threshold=64):
        raise NotImplementedError


class RandomResampler(Resampler):
    @staticmethod
    def upsample(slices, threshold=64):
        original_num = len(slices)
        d = threshold - original_num
        tmp = []
        idxs = []
        for _ in range(d):
            idx = random.randint(0, original_num-1)
            idxs.append(idx)
        for idx, value in enumerate(slices):
            tmp.append(value)
            while idx in idxs:
                idxs.remove(idx)
                tmp.append(value)
        return tmp

    @staticmethod
    def undersample(slices, threshold=64):
        original_num = len(slices)
        d = original_num - threshold
        tmp = slices.copy()
        for _ in range(d):
            idx = random.randint(0, len(tmp)-1)
            tmp.pop(idx)
        return tmp

class SystematicResampler(Resampler):
    '''
    Examples:
        ```
        a = list(range(7))
        re = SystematicResampler()
        re.resample(a,15) # [0, 0, 1, 1, 2, 2, 3, 3, 3, 4, 4, 5, 5, 6, 6]
        re.resample(a,10) # [0, 1, 1, 2, 3, 3, 4, 5, 5, 6]
        re.resample(a,3) # [2, 4, 6]

        ```
    '''
    @staticmethod
    def upsample(slices, threshold=64):
        tmp = []
        original_num = len(slices)
        add_num = threshold - original_num
        add_idxs = list(range(original_num))
        repetitions = add_num / len(slices)
        if add_num % original_num == 0:
            repetitions = add_num // original_num
        else:
            repetitions = add_num // original_num + 1

        if repetitions > 1:
            for _ in range(repetitions-1): add_idxs.extend(list(range(original_num)))

        remain_num = threshold - len(add_idxs)
        if remain_num == 0:
            for idx in sorted(add_idxs):
                tmp.append(slices[idx])
            return tmp
        else:
            interval = original_num // remain_num
            idx = original_num // 2 if original_num%2==1 else original_num//2 -1
            remain_list = [idx]
            count = 1
            flag = 'right'
            while len(remain_list) < remain_num:
                if flag == 'right':
                    idx = idx + count * interval
                    flag = 'left'
                elif flag == 'left':
                    idx = idx - count * interval
                    flag = 'right'
                count += 1
                remain_list.append(idx)
            add_idxs.extend(remain_list)
            for idx in sorted(add_idxs):
                tmp.append(slices[idx])
            return tmp

    @staticmethod
    def undersample(slices, threshold=64):
        d = int(len(slices)/threshold)
        tmp = []
        index = d
        while len(tmp) < threshold:
            tmp.append(slices[index])
            index += d
        return tmp
