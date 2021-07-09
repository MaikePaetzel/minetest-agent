
from agent.RobSandBox import Entity
from agent.RobSandBox.MoveEnvironment import Env
from tensorforce.execution import Runner
from tensorforce import Agent, Environment, Runner

env= Env(10,10,10,rand_obj=True, rand_init_pos=True)


print(env.states())

agent = Agent.create(
    agent='dqn', 
    environment=env, 
    memory=5000, 
    batch_size=1,
    exploration=0.1
)


runner = Runner(
    agent=agent,
    environment=env,
    max_episode_timesteps=500
)

runner.run(num_episodes=100,evaluation=True)
runner.close()