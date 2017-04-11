import numpy as np
import os
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import confusion_matrix

"""
path and batch size need to be re-specified


"""
data_path = "../data/"
batch_size_train = 1000
batch_size_test = 1000
d = 3
num_embeddings = 300

"""
input format: (id1, id2, label)
embedding format: (id em[1] em[2] ...)

"""

def load_train_test(data_path):
	train = np.loadtxt(os.path.join(data_path,"train"))
	test = np.loadtxt(os.path.join(data_path,"test"))

	train_x = train[:,:train.shape[1]-1]
	train_y = train[:,train.shape[1]-1]

	test_x = test[:,:test.shape[1]-1]
	test_y = test[:,test.shape[1]-1]

	return train_x, train_y, test_x, test_y

def giveBatchIndices(batchSize, nRows):
    indices = range(nRows)
    np.random.shuffle(indices)
    ret = []
    start = 0
    while start < nRows:
        ret.append(indices[start:(start+batchSize)])
        start += batchSize
    return ret

def get_batch_features(train_x, train_y, test_x, test_y, embeddings, batch_indices_train, batch_indices_test):

	train_ids = train_x[batch_indices_train,:].astype(int)
	train_labels = train_y[batch_indices_train]

	test_ids = test_x[batch_indices_test,:].astype(int)
	test_labels = test_y[batch_indices_test]

	vecs1_train = embeddings[train_ids[:,0],:]
	vecs2_train = embeddings[train_ids[:,1],:]

	vecs1_test = embeddings[test_ids[:,0],:]
	vecs2_test = embeddings[test_ids[:,1],:]

	train_features = np.sum(vecs1_train*vecs2_train, axis = 1)
	test_features = np.sum(vecs1_test*vecs2_test, axis = 1)

	return np.expand_dims(train_features,1), train_labels,np.expand_dims(test_features,1), test_labels

def train_and_test_on_batch(model, train_x, train_y, test_x, test_y, embeddings, batch_indices_train, batch_indices_test, confusion_mat = False):
	train_features, train_labels,test_features, test_labels = get_batch_features(train_x, train_y, test_x, test_y, embeddings, batch_indices_train, batch_indices_test)
	model.partial_fit(train_features, train_labels, [0,1])

	predictions = model.predict(test_features)

	if confusion_mat:
		print confusion_matrix(test_labels, predictions, labels = [0,1])

	print "accuracy: ", model.score(test_features, test_labels)


def train_and_test(data_path):
	train_x, train_y, test_x, test_y = load_train_test(data_path)
	model = SGDClassifier()

	indices_bag_train = giveBatchIndices(batch_size_train, train_x.shape[0])
	indices_bag_test = giveBatchIndices(batch_size_test, test_x.shape[0])
	
	embeddings_data = np.loadtxt(os.path.join(data_path, "embeddings"))
	node_ids = embeddings_data[:,0].astype(int)
	node_embeddings = embeddings_data[:,1:]
	embeddings = np.zeros((embeddings_data.shape[0], embeddings_data.shape[1]-1))
	embeddings[node_ids,:] = node_embeddings

	for i in xrange(len(indices_bag_train)):
		for j in xrange(len(indices_bag_test)):
			train_and_test_on_batch(model, train_x, train_y, test_x, test_y, embeddings, indices_bag_train[i], indices_bag_test[j])

def generate_fake_data(data_path):
	id1 = np.random.randint(0,num_embeddings-1,batch_size_train)
	id2 = np.random.randint(0,num_embeddings-1,batch_size_train)
	y = np.random.randint(0,2,batch_size_train)
	data = np.column_stack((id1,id2,y))

	embeddings = np.column_stack((range(num_embeddings),np.random.rand(num_embeddings,d)))
	
	np.savetxt(os.path.join(data_path, "train"), data)
	np.savetxt(os.path.join(data_path, "test"), data)
	np.savetxt(os.path.join(data_path, "embeddings"), embeddings)

if __name__ == "__main__":
	generate_fake_data(data_path)
	train_and_test(data_path)