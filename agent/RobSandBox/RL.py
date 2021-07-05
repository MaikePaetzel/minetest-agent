from tensorflow import keras
from Entity import Entity
from World import Sandbox
import numpy as np

model = keras.Sequential()
model.add(keras.layers.InputLayer(batch_input_shape=(1008,)))
model.add(keras.layers.Dense(10, activation='sigmoid'))
model.add(keras.layers.Dense(11, activation='linear'))
model.compile(loss='mse', optimizer='adam', metrics=['mae'])


def from_obj_to_mat(k,obj):
    
    if k == 'player_position':
        mat = np.zeros((5,1))
        mat[0][0] = 1
        mat[1][0] = obj['objectiv'][0]
        mat[2][0] = obj['objectiv'][1]
        mat[3][0] = obj['objectiv'][2]
        mat[4][0] = 10
    return mat


def obj_to_gmatrix(dic):
    fs = False
    ret = None
    for k in dic:
        # print(ret)
        if fs:
            ret = np.concatenate((ret, from_obj_to_mat(k,dic[k])),axis=1)
        else :
            fs = True
            ret = from_obj_to_mat(k,dic[k])
    return ret


# Scenario 1 -> Moving to somewhere
def env():
    objective_dic = {
        'player_position' : { # 1
            'objectiv' :(5,4,5),
            'reward' : 1
        }
    }
    obj_mat = obj_to_gmatrix(objective_dic)
    world = Sandbox(10,10,10)
    world.add_player(1,5,1)
    return obj_mat,world



def is_done(world, obj):
    if world.player.x == obj[1][0] and  world.player.x == obj[2][0] and  world.player.x == obj[3][0]:
        return 10,True
    else :
        return 0,False


y = 0.95
eps = 0.5
decay_factor = 0.999
r_avg_list = []

for i in range(10):
    obj,world = env()
    eps *= decay_factor
    if i % 100 == 0:
        print("Episode {} of {}".format(i + 1, 10))
    done = False
    r_sum = 0
    while not done:
        if np.random.random() < eps:
            a = np.random.randint(0, 11)
        else:
            print(model.predict(np.concatenate((world.world.reshape(-1),obj.reshape(-1),np.array([world.player.x,world.player.y,world.player.z])))).shape)
            a = np.argmax(model.predict(np.concatenate((world.world.reshape(-1),obj.reshape(-1),np.array([world.player.x,world.player.y,world.player.z])))))
        print(a)
        r,done = is_done(world,obj)
        target = r + y *np.argmax(model.predict(np.concatenate((world.world.reshape(-1),obj.reshape(-1),np.array([world.player.x,world.player.y,world.player.z])))))
        target_vec = model.predict(np.concatenate((world.world.reshape(-1),obj.reshape(-1),np.array([world.player.x,world.player.y,world.player.z]))))[0]
        print(target_vec)
        target_vec[a] = target
        model.fit(np.identity(5)[s:s + 1], target_vec.reshape(-1, 2), epochs=1, verbose=0)
        # s = new_s
        r_sum += r
    r_avg_list.append(r_sum / 1000)


