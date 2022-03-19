import os
import sys
import numpy as np
from torch.utils.data import Dataset

Cross_Subject = [1, 2, 4, 5, 8, 9, 13, 14, 15, 16, 17, 18, 19, 25, 27, 28, 31, 34, 35, 38]

class NTU60SubjectCL(Dataset):
    def __init__(self, root, meta, frames_per_clip=23, step_between_clips=2, num_points=2048, train=True):
        super(NTU60SubjectCL, self).__init__()

        self.videos = []
        self.labels = []
        self.index_map = []
        self.nframes = []
        # self.ts = []
        index = 0

        with open(meta, 'r') as f:
            for line in f:
                outs = line.split()
                name, nframes, group = outs[0], outs[1], outs[2]
                name = name.split('/')[-1]
                subject = int(name[9:12])
                if train:
                    if subject in Cross_Subject:
                        label = int(name[-3:]) - 1
                        nframes = int(nframes)
                        
                        
                        if len(self.labels) == int(group):
                            index += 1
                            self.labels.append([label])
                            self.videos.append([os.path.join(root, name+'.npz')])
                            self.nframes.append([nframes])
                        else:
                            self.labels[-1].append(label)
                            self.videos[-1].append(os.path.join(root, name+'.npz'))
                            self.nframes[-1].append(nframes)

                        
                        # self.labels.append(label)
                        # self.videos.append(os.path.join(root, name+'.npz'))
                    else:
                        assert False
                else:
                    if True:
                    # if subject not in Cross_Subject:
                        label = int(name[-3:]) - 1
                        nframes = int(nframes)
                        for t in range(0, nframes-step_between_clips*(frames_per_clip-1), step_between_clips):
                            self.index_map.append((index, t))
                        index += 1
                        self.labels.append(label)
                        self.videos.append(os.path.join(root, name+'.npz'))

        self.videos_temp = []
        index = 0
        for i, video in enumerate(self.videos):
            if len(video) == 3:
                self.videos_temp.append(video)
                nframes = min(min(self.nframes[i][0], self.nframes[i][1]), self.nframes[i][2])
                for t in range(0, nframes-step_between_clips*(frames_per_clip-1), step_between_clips):
                    self.index_map.append((index, t))
                index += 1
        self.videos = self.videos_temp
        print(self.videos)
        self.frames_per_clip = frames_per_clip
        self.step_between_clips = step_between_clips
        self.num_points = num_points
        self.train = train
        self.num_classes = 60 # max(self.labels) + 1
        print(len(self.index_map))


    def __len__(self):
        return len(self.index_map)

    def __getitem__(self, idx):
        index1, t1 = self.index_map[idx]

        # if len(self.videos[index]) < 3:
        #     return self.__getitem__(index + 1)
        # video = np.random.choice(self.videos[index], 2, replace=False)
        # assert video[0] != video[1]
        videos = self.videos[index1]
        
        def load_clip(video, t):
            # while True:
            #     try:
            video = np.load(video, allow_pickle=True)['data'] * 100
            clip = [video[t+i*self.step_between_clips] for i in range(self.frames_per_clip)]
            #         break
            #     except:
                    
            #         # index, t = self.index_map[np.random.randint(0, len(self.index_map))]
            #         video = self.videos[idx]
                #    print(index)
                
            # label = self.labels[index]

            # clip = [video[t+i*self.step_between_clips] for i in range(self.frames_per_clip)]
            for i, p in enumerate(clip):
                if p.shape[0] > self.num_points:
                    r = np.random.choice(p.shape[0], size=self.num_points, replace=False)
                else:
                    repeat, residue = self.num_points // p.shape[0], self.num_points % p.shape[0]
                    r = np.random.choice(p.shape[0], size=residue, replace=False)
                    r = np.concatenate([np.arange(p.shape[0]) for _ in range(repeat)] + [r], axis=0)
                clip[i] = p[r, :]
            clip = np.array(clip)

            if self.train:
                # scale the points
                scales = np.random.uniform(0.9, 1.1, size=3)
                clip = clip * scales

            return clip
        
        clip1 = load_clip(videos[0], t1)
        clip2 = load_clip(videos[1], t1)
        clip3 = load_clip(videos[2], t1)

        return clip1.astype(np.float32), clip2.astype(np.float32), clip3.astype(np.float32)

if __name__ == '__main__':
    dataset = NTU60Subject(root='/scratch/HeheFan-data/data/ntu/video', meta='/scratch/HeheFan-data/data/ntu/ntu60.list', frames_per_clip=16)
    clip, label, video_idx = dataset[0]
    data = clip[0]
    print(data[:,0].max()-data[:,0].min())
    print(data[:,1].max()-data[:,1].min())
    print(data[:,2].max()-data[:,2].min())
    #print(clip)
    print(label)
    print(video_idx)
    print(dataset.num_classes)
