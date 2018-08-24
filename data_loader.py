import scipy
from glob import glob
import numpy as np
import matplotlib.pyplot as plt
import nibabel as nib
from scipy.ndimage import zoom
min_voxel_value = 0
max_voxel_value = 5653.5
class DataLoader(object):
    def __init__(self, img_h_res, img_l_res):
        self.h_img_res = img_h_res
        self.l_img_res = img_l_res

    def get_res_low_from_origin(self, img_h):
        res = []
        data = np.copy(img_h)
        x_l, _, _ = self.l_img_res
        x_h, _, _ = self.h_img_res
       	step = x_h//x_l
        start = 0
        for i in range(x_l):
            start += step
            res.append(data[start])
        return np.array(res)
        # return zoom(data, (x/x_raw, y/y_raw, z/z_raw))

    def get_low_res_file_with_affine(self, data, info, shape):
        affine = np.eye(4)
        affine[0, 0] = shape[0] / data.shape[0]
        test_img = nib.Nifti1Image(data, affine, info.header)
        test_img.update_header()
        return test_img

    def load_data(self, dataset_path, batch_size=1, is_testing=False):
        path = glob(dataset_path, recursive=True)
        batch_images = np.random.choice(path, size=batch_size)

        imgs_hr = []
        imgs_lr = []
        imgs_info = []
        imgs_path = []
        imgs_shape = []
        for img_path in batch_images:
            img_info, h_img = self.imread(img_path)
            if is_testing:
                h_img = test_preprocessing(h_img)
            x_raw, y_raw, z_raw = h_img.shape
            x, y, z = self.h_img_res
            if is_testing:
                h_img_stand = h_img
                l_img_stand = h_img
            else:
                h_img_stand = zoom(h_img, (x/x_raw, y/y_raw, z/z_raw))
                l_img_stand = self.get_res_low_from_origin(h_img_stand)
            imgs_hr.append(h_img_stand)
            imgs_lr.append(l_img_stand)
            imgs_info.append(img_info)
            imgs_shape.append(h_img.shape)
            imgs_path.append(img_path)

        average = max_voxel_value/2
        imgs_hr = np.array(imgs_hr) / average - 1.
        imgs_lr = np.array(imgs_lr) / average - 1.
        return imgs_hr, imgs_lr, imgs_info, imgs_shape, imgs_path


    def imread(self, path):
        mri_image = nib.load(path)
        mri_image_data = mri_image.get_fdata()
        return mri_image, mri_image_data

def test_preprocessing(X):
    x,y,z,_ = X.shape
    X = np.reshape(X, (x,y,z))
    X = np.rot90(X, 1, axes=(0,2))
    X = np.rot90(X, 2, axes=(1,2))
    return X

def show_slices(slices):
    fig,axes = plt.subplots(len(slices), 1, figsize=(16, 16))
    for i,slice in enumerate(slices):
        axes[i].imshow(slice.T, cmap="gray", origin="lower")

