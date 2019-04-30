"""
The main entry point of the speaker clustering suite.
You can use this file to setup, train and test any network provided in the suite.

Usage: controller.py [-h] [-setup] [-n NETWORK] [-train] [-test] [-clear]
                     [-debug]

Controller suite for Speaker clustering

optional arguments:
  -h, --help  show this help message and exit
  -setup      Run project setup.
  -n NETWORK  The network to use for training or analysis.
  -train      Train the specified network.
  -test       Test the specified network.
  -clear      Clean directories before starting network.
  -debug      Set loglevel for TensorFlow and Logger to debug.
  -plot       Plots the last results of the specified networks in one file.

"""
import argparse
import sys

import matplotlib
matplotlib.use('Agg')


from common.analysis.analysis import *
from common.extrapolation.setup import setup_suite, is_suite_setup
from common.network_controller import NetworkController
from common.utils.paths import *

# Controllers
# -------------------
# from networks.flow_me.me_controller import MEController
# from networks.lu_vo.luvo_controller import LuvoController
# from networks.pairwise_kldiv.kldiv_controller import KLDivController

# Constants
# -------------------
DEFAULT_SETUP = False
DEFAULT_NETWORK = 'pairwise_lstm_vox2'
DEFAULT_TRAIN = False
DEFAULT_TEST = False
DEFAULT_CLEAR = False
DEFAULT_DEBUG = False
DEFAULT_PLOT = False
DEFAULT_BEST = False
DEFAULT_VAL_NUMBER = 40
DEFAULT_OUT_LAYER = 2
DEFAULT_SEG_SIZE = 15
DEFAULT_VEC_SIZE = 512
DEFAULT_ACTIVELEARNING_ROUNDS = 50
DEFAULT_EPOCHS = 1000
DEFAULT_DENSE_FACTOR = 100

class Controller(NetworkController):
    def __init__(self,
                 setup=DEFAULT_SETUP, network=DEFAULT_NETWORK, train=DEFAULT_TRAIN, test=DEFAULT_TEST,
                 clear=DEFAULT_CLEAR, debug=DEFAULT_DEBUG, plot=DEFAULT_PLOT, best=DEFAULT_BEST,
                 val_number=DEFAULT_VAL_NUMBER, out_layer=DEFAULT_OUT_LAYER, seg_size=DEFAULT_SEG_SIZE,
                 vec_size=DEFAULT_VEC_SIZE, active_learning_rounds=DEFAULT_ACTIVELEARNING_ROUNDS,
                 epochs=DEFAULT_EPOCHS, dense_factor=DEFAULT_DENSE_FACTOR):
        super().__init__("Front", "speakers_40_clustering_vs_reynolds")
        self.setup = setup
        self.network = network
        self.train = train
        self.test = test
        self.clear = clear
        self.debug = debug
        self.network_controllers = []
        self.plot = plot
        self.best = best
        self.out_layer = out_layer
        self.seg_size = seg_size
        self.vec_size = vec_size
        self.active_learning_rounds = active_learning_rounds
        self.epochs = epochs
        self.dense_factor = dense_factor

        validation_data = {
            40: "speakers_40_clustering_vs_reynolds",
            60: "speakers_60_clustering",
            80: "speakers_80_clustering"
        }

        self.val_data = validation_data[val_number]

    def train_network(self):
        for network_controller in self.network_controllers:
            network_controller.train_network()

    def test_network(self):
        for network_controller in self.network_controllers:
            network_controller.test_network(self.out_layer, self.seg_size, self.vec_size)

    def get_embeddings(self):
        return None, None, None, None

    def run(self):

        # Setup
        if self.setup:
            self.setup_networks()

        # Validate network
        self.generate_controllers()

        # Train network
        if self.train:
            self.train_network()

        # Test network
        if self.test:
            self.test_network()

        # Plot resultsit b
        if self.plot:
            self.plot_results()

    def generate_controllers(self):
        self.network_controllers = []
        if self.network == 'pairwise_lstm_vox2':
            from networks.pairwise_lstm_vox.lstm_controller import LSTMVOX2Controller
            self.network_controllers.append(
                LSTMVOX2Controller(
                    self.out_layer, 
                    self.seg_size, 
                    self.vec_size, 
                    self.active_learning_rounds,
                    self.epochs,
                    self.dense_factor
                )
            )
        if self.network == 'pairwise_lstm':
            from networks.pairwise_lstm.lstm_controller import LSTMController
            self.network_controllers.append(
                LSTMController(
                    self.out_layer, 
                    self.seg_size, 
                    self.vec_size, 
                    self.epochs
                )
            )
        if self.network == 'arc_face':
            from networks.lstm_arc_face.arc_face_controller import ArcFaceController
            self.network_controllers.append(ArcFaceController())


    def setup_networks(self):
        if is_suite_setup():
            print("Already fully setup.")
        else:
            print("Setting up the network suite.")

        setup_suite()

    def plot_results(self):
        plot_files(self.network, self.get_result_files())

    def get_result_files(self):
        if self.network == "all":
            regex = '*best*.pickle'
        elif self.best:
            regex = self.network + '*best*.pickle'
        else:
            # TODO: Funktioniert aktuell nicht ohne "-best" Flag
            #regex = self.network + ".pickle"
            regex = self.network + '*best*.pickle'


        files = list_all_files(get_results(), regex)

        for index, file in enumerate(files):
            files[index] = get_results(file)
        return files

if __name__ == '__main__':
    # Parse console Args
    parser = argparse.ArgumentParser(description='Controller suite for Speaker clustering')
    # add all arguments and provide descriptions for them
    parser.add_argument('-setup', dest='setup', action='store_true',
                        help='Run project setup.')
    parser.add_argument('-n', dest='network', default=DEFAULT_NETWORK,
                        help='The network to use for training or analysis.')
    parser.add_argument('-train', dest='train', action='store_true',
                        help='Train the specified network.')
    parser.add_argument('-test', dest='test', action='store_true',
                        help='Test the specified network.')
    parser.add_argument('-clear', dest='clear', action='store_true',
                        help='Clean directories before starting network.')
    parser.add_argument('-debug', dest='debug', action='store_true',
                        help='Set loglevel for TensorFlow and Logger to debug')
    parser.add_argument('-plot', dest='plot', action='store_true',
                        help='Plots the last results of the specified networks in one file.')
    parser.add_argument('-best', dest='best', action='store_true',
                        help='If a single Network is specified and plot was called, just the best curves will be plotted')
    parser.add_argument('-val#', dest='validation_number', default=DEFAULT_VAL_NUMBER,
                        help='Specify how many speakers should be used for testing (40, 60, 80).')
    parser.add_argument('-out_layer#', dest='out_layer', default=DEFAULT_OUT_LAYER,
                        help='Output layer')
    parser.add_argument('-seg_size#', dest='seg_size', default=DEFAULT_SEG_SIZE,
                        help='Segment size')
    parser.add_argument('-vec_size#', dest='vec_size', default=DEFAULT_VEC_SIZE,
                        help='Vector size')
    parser.add_argument('-alr#', dest='active_learning_rounds', default=DEFAULT_ACTIVELEARNING_ROUNDS,
                        help='Active learning rounds (only used by VOX2 currently)')
    parser.add_argument('-e#', dest='epochs', default=DEFAULT_EPOCHS,
                        help='Number of epochs to train in total')
    parser.add_argument('-df#', dest='dense_factor', default=DEFAULT_DENSE_FACTOR,
                        help='Factor for dense layer multiplication (Vox2 only)')

    args = parser.parse_args()
    #print(args)

    controller = Controller(
        setup=args.setup, network=args.network, train=args.train, test=args.test, 
        clear=args.clear, debug=args.debug, plot=args.plot, best=args.best, 
        val_number=args.validation_number, out_layer=int(args.out_layer), 
        seg_size=int(args.seg_size), vec_size=int(args.vec_size),
        active_learning_rounds=int(args.active_learning_rounds),
        epochs=int(args.epochs), dense_factor=int(args.dense_factor)
    )

    controller.run()
