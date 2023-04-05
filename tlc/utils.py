from .models import *
import numpy as np
import pydicom
import os
import scipy.ndimage
from sklearn.cluster import KMeans
from skimage.morphology import disk
from skimage import measure
from scipy import ndimage as ndi
import matplotlib.pyplot as plt
import scipy.misc
from glob import glob
def load_data(url, user, urlk):
    #link to the ct images folder
    data_path = url
    #export result to other folder
    output_path = working_path ='./media'
    #open dicom files
    g = glob(data_path+'/*.dcm')
    #loop over the image files and store everything into a list
    def load_scan(path):
        # os.listdir(path) = name of all files in path
        # dicom_read_file() get the dataset of ct image in string type
        slices = [pydicom.read_file(path + '/' + s) for s in os.listdir(path)]
        # order the list by the increasement of instancenumber
        # [(0020,0013),(0020,0011),(0020,0015)]->[(0020,0011),(0020,0013),(0020,0015)]
        slices.sort(key=lambda x: int(x.InstanceNumber))
        # if 'try' fail or error, 'except' code will be operated
        try:
            # Position coordinate [x,y,z] , ImagePositionPatient[2] get the z coordinate
            # abs absolute value
            slice_thickness = np.abs(slices[0].ImagePositionPatient[2] - slices[1].ImagePositionPatient[2])
        except:
            slice_thickness = np.abs(slices[0].SliceLocation - slices[1].SliceLocation)
        for s in slices:
            s.SliceThickness = slice_thickness
        return slices

    # convert raw values of voxel in the images to HU
    def get_pixels_hu(scans):
        # s.pixel_array get ct image's pixel data in matrix
        # np.stack join many array(matrix) with the same dimension into new sequence
        image = np.stack([s.pixel_array for s in scans])
        # should be possible as values should always be low enough (<32k)
        # convert all dataframe columns into dtype int16
        image = image.astype(np.int16)
        # Set outside-of-scan pixels (HU = -2000) to 0
        # The intercept(threshold) is usually -1024, so air is approximately 0
        image[image == -2000] = 0
        # Convert to Hounsfield units (HU=pixel_value*slope+intercept)
        intercept = scans[0].RescaleIntercept if 'RescaleIntercept' in scans[0] else -1024
        slope = scans[0].RescaleSlope if 'RescaleSlope' in scans[0] else 1
        if slope != 1:
            image = slope * image.astype(np.float64)
            image = image.astype(np.int16)
        image += np.int16(intercept)
        return np.array(image, dtype=np.int16)

    def resample(image, scan, new_spacing=[1, 1, 1]):
        # Determine current pixel spacing
        # map(function,iterable) -> return a list,tuple to inform function
        # get scan to be in form of float number
        spacing = [scan[0].SliceThickness, scan[0].PixelSpacing[0], scan[0].PixelSpacing[1]]
        # change list to array
        spacing = np.array(spacing)

        resize_factor = spacing / new_spacing
        new_real_shape = image.shape * resize_factor
        # round after comma ','
        new_shape = np.round(new_real_shape)
        real_resize_factor = new_shape / image.shape
        new_spacing = spacing / real_resize_factor
        # change the size of image with a factor
        image = scipy.ndimage.interpolation.zoom(image, real_resize_factor)

        return image, new_spacing

    def make_lungmask(img, display=False):
        row_size = img.shape[0]
        col_size = img.shape[1]
        # compute average value
        mean = np.mean(img)
        # compute standard deviation
        std = np.std(img)
        img = img - mean
        img = img / std
        # Find the average pixel value near the lungs to renormalize washed out images
        middle = img[int(col_size / 5):int(col_size / 5 * 4), int(row_size / 5):int(row_size / 5 * 4)]
        mean = np.mean(middle)
        max = np.max(img)
        min = np.min(img)
        # To improve threshold finding, moving the underflow and overflow on the pixel spectrum
        img[img == max] = mean
        img[img == min] = mean

        # Using Kmeans to separate foreground (soft tissue / bone) and background (lung/air) -> cluster = 2
        # np.reshape(reshaped array, newshape (row,col))
        # np.prod() return number of elements in array
        # np.reshape(middle,[np.prod(middle.shape),1] change the array into [elementsx1] size
        kmeans = KMeans(n_clusters=2).fit(np.reshape(middle, [np.prod(middle.shape), 1]))
        # cluster_centers_: array(n.o cluster, n.o features) Coordinates of cluster centers.
        # .flatten() return array to one dimension
        # sorted() sort array from 1->n, alphabet a,b,c,d,...
        centers = sorted(kmeans.cluster_centers_.flatten())
        threshold = np.mean(centers)
        # np.where(condition, true, else) if img<threshold, img =1, else = 0
        thresh_img = np.where(img < threshold, 1.0, 0.0)  # threshold the image
        # Different labels are displayed in different colors
        labels = measure.label(thresh_img)
        # np.unique() sorted unique elements of array
        label_vals = np.unique(labels)
        # Measure properties of labeled image regions.
        regions = measure.regionprops(labels)
        good_labels = []
        for prop in regions:
            # bbbox(bounding box):tuple (min_row, min_col, max_row, max_col)
            B = prop.bbox
            C = prop.area
            if B[0] > 0 and B[1] > 0 and C > 500 and B[2] < img.shape[0] and B[3] < img.shape[1] - 10:
                # label: int the label in labeled input img
                good_labels.append(prop.label)
        mask = np.ndarray([row_size, col_size], dtype=np.int8)
        mask[:] = 0

        #  After just the lungs are left, we do another large dilation in order to fill in and out the lung mask
        for N in good_labels:
            mask = mask + np.where(labels == N, 1, 0)
        selem = disk(5)
        final_mask = ndi.binary_fill_holes(mask)
        original_mask = img * thresh_img * mask
        original_mask = np.where(original_mask != 0, 1, 0)
        new_label = measure.label(original_mask)
        # mask = morphology.dilation(mask,np.ones(3,3])) # one last dilation
        if (display):
            fig, ax = plt.subplots(3, 2, figsize=[12, 12])
            ax[0, 0].set_title("Original")
            ax[0, 0].imshow(img, cmap='gray')
            ax[0, 0].axis('off')
            ax[0, 1].set_title("Threshold")
            ax[0, 1].imshow(thresh_img, cmap='gray')
            ax[0, 1].axis('off')
            ax[1, 0].set_title("Color Labels")
            ax[1, 0].imshow(labels)
            ax[1, 0].axis('off')
            ax[1, 1].set_title("Good Labels")
            ax[1, 1].imshow(mask, cmap='gray')
            ax[1, 1].axis('off')
            ax[2, 0].set_title("Final Mask")
            ax[2, 0].imshow(final_mask, cmap='gray')
            ax[2, 0].axis('off')
            ax[2, 1].set_title("Apply Mask on Original")
            ax[2, 1].imshow(new_label, cmap='gray')
            ax[2, 1].axis('off')
            plt.show()
        return final_mask
        # return mask

    def shallowest_lung(lung_mask, min_row, min_col, max_row, max_col):
        col_size = []
        dis = int((max_col - min_col) / 10)
        for i in range(min_col + dis, max_col - dis):
            a = 0
            for j in range(min_row, max_row + 1):
                if lung_mask[j][i] == 1:
                    a += 1
            col_size.append(a)
        mincol_index = min_col + dis + col_size.index(min(col_size))
        for k in range(min_row, max_row + 1):
            if lung_mask[k][mincol_index] == 1:
                break
        minrow_index = k
        return mincol_index, minrow_index

    # for connected mask only
    def connected_region(img_connected, img_original):
        row = img_connected.shape[0]
        col = img_connected.shape[1]
        label_img = measure.label(img_connected)
        label_vals = np.unique(label_img)
        regions = measure.regionprops(label_img)
        for prop in regions:
            box = prop.bbox
            lung_area = prop.area
        right_mask = np.ndarray([row, col], dtype=np.int8)
        right_mask[:] = 0
        good_labels = []
        col_min, row_min = shallowest_lung(img_connected, box[0], box[1], box[2], box[3])
        max_row = min([int(row_min + row / 10), row])
        min_col = max([int(col_min - col / 15), 0])
        max_col = min([int(col_min + col / 10), col])
        new_mask = np.zeros((row, col))
        for j in range(box[0], max_row):
            for k in range(min_col, max_col):
                if img_connected[j][k] == 1:
                    new_mask[j][k] = 1
        new_img = img_original * new_mask
        number = []
        for i in new_img:
            for j in i:
                if j != 0:
                    number.append(j)
        mean = np.mean(number)
        if mean == 0 or lung_area < 6000:
            if box[1] < col / 2 and box[3] < col * 8 / 10:
                good_labels.append(prop.label)
            for N in good_labels:
                right_mask = right_mask + np.where(label_img == N, 1, 0)
            right_mask = np.where(right_mask != 0, 1, 0)
            new_img = img_connected
        else:
            i = 0
            new_label = np.ndarray([row, col], dtype=np.int8)
            while len(label_vals) == 2 and i < 20:
                new_img = np.where(new_img < mean, 1, 0)
                diff = (new_img > 0) ^ (new_mask > 0)
                diff = np.where(diff == 1, 0, 1)
                selem = disk(10)
                new_img = img_connected * diff
                new_img = ndi.binary_fill_holes(new_img)
                test_label = measure.label(new_img)
                label_vals = np.unique(test_label)
                if len(label_vals) != 2:
                    region = measure.regionprops(test_label)
                    for prop in region:
                        A = prop.area
                        if A < 100:
                            new_label = np.where(test_label == prop.label, 0, test_label)
                    label_vals = np.unique(new_label)
                mean -= 10
                i += 1
            if len(label_vals) == 2:
                region = measure.regionprops(test_label)
                for prop in region:
                    B = prop.bbox
                mincol, minrow = shallowest_lung(new_img, B[0], B[1], B[2], B[3])
                for i in range(0, mincol):
                    for k in range(0, row):
                        if new_img[k][i] == 1:
                            right_mask[k][i] = 1
            else:
                region = measure.regionprops(test_label)
                for prop in region:
                    B = prop.bbox
                    if B[1] < col / 2 and B[3] < col * 7 / 10:
                        good_labels.append(prop.label)
                for N in good_labels:
                    right_mask = right_mask + np.where(test_label == N, 1, 0)
                right_mask = np.where(right_mask != 0, 1, 0)
        return right_mask, new_img

    def divide_lung(img_original, display=False):
        img = make_lungmask(img_original)
        row = img.shape[0]
        col = img.shape[1]
        label_img = measure.label(img)
        label_vals = np.unique(label_img)
        regions = measure.regionprops(label_img)
        good_labels = []
        right_mask = np.ndarray([row, col], dtype=np.int8)
        right_mask[:] = 0
        left_mask = np.ndarray([row, col], dtype=np.int8)
        left_mask[:] = 0
        box = []
        label_part = []
        if len(label_vals) == 3:
            for prop in regions:
                box.append(prop.bbox)
                label_part.append(prop.label)
            if box[0][1] < box[1][1]:
                good_labels.append(label_part[0])
            else:
                good_labels.append(label_part[1])
            for N in good_labels:
                right_mask = right_mask + np.where(label_img == N, 1, 0)
                right_mask = np.where(right_mask != 0, 1, 0)
            left_mask = img - right_mask

        if len(label_vals) > 3:
            for prop in regions:
                B = prop.bbox
                if B[0] > 0 and B[1] > 0 and B[2] < row and B[1] < col * 4 / 10 and B[3] < col * 7 / 10:
                    # label: int the label in labeled input img
                    good_labels.append(prop.label)
                for N in good_labels:
                    right_mask = right_mask + np.where(label_img == N, 1, 0)
                    right_mask = np.where(right_mask != 0, 1, 0)
                left_mask = img - right_mask

        if len(label_vals) == 2:
            right_mask, img = connected_region(img, img_original)
            left_mask = img - right_mask
        if (display):
            fig, ax = plt.subplots(3, 2, figsize=[12, 12])
            ax[0, 0].set_title("Original")
            ax[0, 0].imshow(img_original, cmap='gray')
            ax[0, 0].axis('off')
            ax[0, 1].set_title("Label")
            ax[0, 1].imshow(img, cmap='gray')
            ax[0, 1].axis('off')
            ax[1, 0].set_title("Distance")
            ax[1, 0].imshow(label_img)
            ax[1, 0].axis('off')
            ax[1, 1].set_title("Label")
            ax[1, 1].imshow(img, cmap='gray')
            ax[1, 1].axis('off')
            ax[2, 0].set_title("Right mask")
            ax[2, 0].imshow(right_mask, cmap='gray')
            ax[2, 0].axis('off')
            ax[2, 1].set_title("Left mask")
            ax[2, 1].imshow(left_mask, cmap='gray')
            ax[2, 1].axis('off')
            plt.show()
        return img, right_mask, left_mask

    def measure_lung(img, px=0):
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                if img[i][j] == 1:
                    px += 1
        return px
    def make_mesh(original_img, mask_img, threshold=-300, step_size=1):
        print("Transposing surface")
        # reorder matrix (0,1,3) -> transpose(2,1,0) -> (3,1,0)
        image = original_img * mask_img
        # p = image.transpose(2,1,0)
        print("Calculating surface")
        # get the coordinate of each surface(slices) in 3D volume: vertice, face(triangle x,y,z)
        # all in (x,3) dimension
        # The threshold of -300 HU is fine for visualizing chest CT scans
        verts, faces, norm, val = measure.marching_cubes(image, threshold, step_size=step_size,
                                                                 allow_degenerate=True)
        return verts, faces

    id = 1
    patient = load_scan(data_path)
    imgs = get_pixels_hu(patient)
    # save an array to a numpy file (.npy) format
    np.save(output_path + "fullimages_%d.npy" % (id), imgs)
    file_used = output_path + "fullimages_%d.npy" % id
    imgs_to_process = np.load(file_used).astype(np.float64)
    # each slice is resampled in 1x1x1 mm pixels and slices.
    imgs_after_resamp, spacing = resample(imgs_to_process, patient, [1, 1, 1])
    new_size = imgs_after_resamp.shape
    mask_stack = np.zeros((imgs_after_resamp.shape[0], imgs_after_resamp.shape[1], imgs_after_resamp.shape[2]))
    leftmask_stack = np.zeros((imgs_after_resamp.shape[0], imgs_after_resamp.shape[1], imgs_after_resamp.shape[2]))
    rightmask_stack = np.zeros((imgs_after_resamp.shape[0], imgs_after_resamp.shape[1], imgs_after_resamp.shape[2]))
    i = 0
    volume = 0
    right_mask = 0
    left_mask = 0
    for img in imgs_after_resamp:
        mask_stack[i], rightmask_stack[i], leftmask_stack[i] = divide_lung(img)
        mask_stack[i] = np.where(mask_stack[i] != 0, 1.0, 0.0)
        rightmask_stack[i] = np.where(rightmask_stack[i] != 0, 1.0, 0.0)
        leftmask_stack[i] = np.where(leftmask_stack[i] != 0, 1.0, 0.0)
        slice_volume = measure_lung(mask_stack[i], 0)
        right_volume = measure_lung(rightmask_stack[i], 0)
        left_volume = measure_lung(leftmask_stack[i], 0)
        right_mask += right_volume
        left_mask += left_volume
        volume += slice_volume
        i += 1

    patient_lung = "patient lung volume is " + str(volume) + " mm^3"
    right_lung = "\nright lung volume is " + str(right_mask) + " mm^3"
    left_lung = "\nleft lung volume is " + str(left_mask) + " mm^3"
    print(patient_lung)
    print(right_lung)
    print(left_lung)
    UserFile = UserUploadedFile.objects.create(patient_id=user , drive_id=0)
    UserFile.save()
    Result = ResultFile.objects.create(upload_file=UserFile, right_lung=right_mask, left_lung=left_mask,
                                       lung_volume=volume, url=urlk)
    Result.save()
    v, f = make_mesh(imgs_after_resamp, mask_stack, -1, 1)
    z = v[f]
    return right_mask, left_mask, volume, z
