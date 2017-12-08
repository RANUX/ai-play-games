import numpy
import scipy.special
import random
import cloudpickle as pickle
import os.path

WIN_WIDTH = 800
OBSTACLE_INITSPEED = 4
OBSTACLE_MAXSIZE = 50

# neural network class definition
class NeuralNetwork:
    
    # initialise the neural network
    def __init__(self, inputnodes, hiddennodes, outputnodes, learningrate):
        # set number of nodes in each input, hidden, output layer
        self.inodes = inputnodes
        self.hnodes = hiddennodes
        self.onodes = outputnodes
        
        # link weight matrices, wih and who
        # weights inside the arrays are w_i_j, where link is from node i to node j in the next layer
        # w11 w21
        # w12 w22 etc 
        self.wih = numpy.random.normal(0.0, pow(self.inodes, -0.5), (self.hnodes, self.inodes))
        self.who = numpy.random.normal(0.0, pow(self.hnodes, -0.5), (self.onodes, self.hnodes))

        # learning rate
        self.lr = learningrate
        
        # activation function is the sigmoid function
        self.activation_function = lambda x: scipy.special.expit(x)
        
        # performance of NN
        self.performance = 0
        pass

    
    # train the neural network
    def train(self, inputs_list, targets_list):
        # convert inputs list to 2d array
        inputs = numpy.array(inputs_list, ndmin=2).T
        targets = numpy.array(targets_list, ndmin=2).T
        
        # calculate signals into hidden layer
        hidden_inputs = numpy.dot(self.wih, inputs)
        # calculate the signals emerging from hidden layer
        hidden_outputs = self.activation_function(hidden_inputs)
        
        # calculate signals into final output layer
        final_inputs = numpy.dot(self.who, hidden_outputs)
        # calculate the signals emerging from final output layer
        final_outputs = self.activation_function(final_inputs)
        
        # output layer error is the (target - actual)
        output_errors = targets - final_outputs
        # hidden layer error is the output_errors, split by weights, recombined at hidden nodes
        hidden_errors = numpy.dot(self.who.T, output_errors)
        
        # update the weights for the links between the hidden and output layers
        self.who += self.lr * numpy.dot((output_errors * final_outputs * (1.0 - final_outputs)), numpy.transpose(hidden_outputs))
        
        # update the weights for the links between the input and hidden layers
        self.wih += self.lr * numpy.dot((hidden_errors * hidden_outputs * (1.0 - hidden_outputs)), numpy.transpose(inputs))
        
        pass

    
    # query the neural network
    def query(self, inputs_list):
        # convert inputs list to 2d array
        inputs = numpy.array(inputs_list, ndmin=2).T
        
        # calculate signals into hidden layer
        hidden_inputs = numpy.dot(self.wih, inputs)
        # calculate the signals emerging from hidden layer
        hidden_outputs = self.activation_function(hidden_inputs)
        
        # calculate signals into final output layer
        final_inputs = numpy.dot(self.who, hidden_outputs)
        # calculate the signals emerging from final output layer
        final_outputs = self.activation_function(final_inputs)
        
        return final_outputs


scorecard = []
input_nodes = 3
hidden_nodes = 3
output_nodes = 1
learning_rate = 0.2
n = None

def loadData(fileName):
  training_data_file = open(fileName, "r")
  training_data_list = training_data_file.readlines()
  training_data_file.close()
  return training_data_list

def trainNN():
  train_data_list = loadData("jumpDataTrain.csv")

  epochs = 7
  for e in range(epochs):
    sh_train_data_list = random.sample(train_data_list, len(train_data_list))
    for record in sh_train_data_list:
        # split the record by the ',' commas
        all_values = record.split(',')
        # scale and shift the inputs
        inputs = numpy.asfarray(all_values[1:])
        # normalize values
        inputs[0] = inputs[0] / WIN_WIDTH + 0.01              # distance to obstacle
        inputs[1] = inputs[1] / OBSTACLE_INITSPEED - 0.01     # obstacle speed
        inputs[2] = inputs[2] / OBSTACLE_MAXSIZE + 0.01       # obstacle size
        targets = numpy.asfarray(all_values[0]) * 0.98 + 0.01 # target train value [0] or [1]
        n.train(inputs, targets)


def testNN():
  scorecard = []
  test_data_list = loadData("jumpDataTest.csv")

  for record in test_data_list:
    all_values = record.split(',')
    target = int(all_values[0])
    inputs = numpy.asfarray(all_values[1:])
    # normalize values
    inputs[0] = inputs[0] / WIN_WIDTH + 0.01
    inputs[1] = inputs[1] / OBSTACLE_INITSPEED - 0.01
    inputs[2] = inputs[2] / OBSTACLE_MAXSIZE + 0.01
    outputs = n.query(inputs)
    
    if (target and outputs[0][0] > 0.7) or (not target and outputs[0][0] <= 0.7):
      scorecard.append(1)
    else:
      scorecard.append(0)
  
  # calculate the performance score, the fraction of correct answers
  scorecard_array = numpy.asarray(scorecard)
  n.performance = scorecard_array.sum() / scorecard_array.size
  print ("performance = ", n.performance)

def main():
  global n
  
  prevNN = None
  if os.path.exists("nn.bin"):
    prevNN = pickle.load(open( "nn.bin", "rb" ))
  else:
    prevNN = type('mockobj', (object,), {'performance': 0.8})()
  
  print("Best previous NN performace: ", prevNN.performance)

  for i in range(0, 10):
    n = NeuralNetwork(input_nodes, hidden_nodes, output_nodes, learning_rate)
    trainNN()
    testNN()
    if n.performance > prevNN.performance:
      binary_file = open('nn.bin',mode='wb')
      pickle.dump(n, binary_file)
      binary_file.close()


if __name__ == '__main__':
  main()