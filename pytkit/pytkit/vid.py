import os
import sys
import cv2
import pdb
import pytkit as pk
from pathlib import Path

import skvideo as sk
import skvideo.io as skvio



class Vid:

    vo_cv2 = None
    """ Video object opened using CV2 """

    writer = None
    """ Video oobject opened using scikit-video. Mainly used for writing """
    
    props = {}
    """ Video properties """

    def __init__(self, pth, mode):
        """
        Parameters
        ----------
        pth : Str
            Full path to video
        mode : Str
            Mode of operation. Can be `write` for write and `read` for read
        """

        # Check if the file exists
        if not pk.fd.check_file_existance(pth) and mode == "read":
            raise Exception(f"Video does not exist \n\t{pth}")

        # Reading
        if mode == "read":
            self.vo_cv2 = cv2.VideoCapture(pth)
            self.props = self._get_video_properties(pth)
            
        elif mode == "write":
            self.writer = skvio.FFmpegWriter(
                pth,
                outputdict={
                    '-vcodec': 'libvpx',
                    '-b': '300000000'
                }
            )
            
        else:
            raise Exception(f"Unknown video mode \n\t{mode}")


    def _get_video_properties(self, vpath):
        """ Returns a dictionary with following video properties,
        1. video_name
        2. video_ext
        3. video_path
        4. frame_rate

        Parameters
        ----------
        vpath: str
            Video file path
        """
        # Get video file name and directory location
        vdir_loc = os.path.dirname(vpath)
        vname, vext = os.path.splitext(os.path.basename(vpath))

        # Read video meta information
        vmeta = skvio.ffprobe(vpath)

        # If it is empty i.e. scikit video cannot read metadata
        # return empty stings and zeros
        if vmeta == {}:
            vprops = {
                'islocal': False,
                'full_path': vpath,
                'name': vname,
                'extension': vext,
                'dir_loc': vdir_loc,
                'frame_rate': 0,
                'duration': 0,
                'num_frames': 0,
                'width': 0,
                'height': 0,
                'frame_dim': None
            }

            return vprops

        # Calculate average frame rate
        fr_str = vmeta['video']['@avg_frame_rate']
        fr = round(int(fr_str.split("/")[0]) / int(fr_str.split("/")[1]))

        # get duration
        vdur = round(float(vmeta['video']['@duration']))

        # get number of frames
        vnbfrms = int(vmeta['video']['@nb_frames'])

        # video width
        width = int(vmeta['video']['@width'])

        # video height
        height = int(vmeta['video']['@height'])

        # Frame dimension assuming color video
        frame_dim = (height, width, 3)

        # Creating properties dictionary
        vprops = {
            'islocal': True,
            'full_path': vpath,
            'name': vname,
            'extension': vext,
            'dir_loc': vdir_loc,
            'frame_rate': fr,
            'duration': vdur,
            'num_frames': vnbfrms,
            'width': width,
            'height': height,
            'frame_dim' : frame_dim
        }

        return vprops

    def get_frame(self, frm_num):
        """
        Returns a frame from video using its frame number

        Parameters
        ----------
        frm_num: int
            Frame number
        """

        # Read video and seek to frame
        self.vo_cv2.set(cv2.CAP_PROP_POS_FRAMES, frm_num)
        _, frame = self.vo_cv2.read()

        # Reset the video reader to starting frame
        self.vo_cv2.set(cv2.CAP_PROP_POS_FRAMES, 0)

        return frame
