# preguntas AIMA

---

## 2.10
**Consider a modified version of the vacuum environment in Excercise 2.8, in which the agent is penalized one point for each movement.**  
**a) Can a simple reflex agent be perfectly rational for this environment? Explain**  
**b) What about a reflex agent with state? Design such an agent.**  
**c) How do your answers to a and b change if the agents percepts give it all the clean/dirty status of every square in the environment?**

### respuesta 
a) No, a simple reflex agent acts only on the currents states (location, status(clean/dirty)) without memory. It cannot know from a local percept alone where the next dirty square is, so it cannot be perfectly rational in all situations.  
b) An agent with memory can keep in mind which squares are already known to be dirty/clean and avoid unnecessary moves, so yes I think a reflex agent can be perfectly rational for this environment.  
Design:  
If current state is dirty -> clean it.  
Else if another square is dirty -> move there  
Else if square is unknow -> move there  
Else -> do nothing
c) A simple reflex agent can be perfectly ration now

---

## 2.11  
**Consider a modified version of the vacuum environment in 2.8, in which the geography of the environment - its extent, boundaries and obstacles - is unknown, as is the initial dirt configuration.**  
**a) Can a simple reflex agent be perfectly rational for this environment? Explain**  
**b) Can a simple reflex agent with a randomized agent function outperform a simple reflex agent? Design such an agent and measure its performance on several environments.**
**c) Can you design an environment in which your randomized agent will perform poorly? Show your results**
**d) Can a reflex agent with state outperform a simple reflex agent? Design such an agent and measure its performance on several environments. Can you design a rational agent of this type?**

### respuesta
a) No,without known geography and placement of dirt, a simple reflex agent without memory cannot operate optimally
b)Yes, I think randomization could outperform a simple reflex agent.  
Design:  
If dirt -> clean  
Else choose a random move (left, right, up, down) in a non blocked direction (if bumps occur, turn around)
c)Long narrow path with occasional but rare side branches  
d) Yes, it prevents unnecessary moves.  
Design:  
if dirt -> clean  
else if dirty cell known -> move there and clean  
else if no information -> move systematically  
else -> do nothing

---

