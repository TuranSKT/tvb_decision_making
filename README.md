# Auditory Discrimination Paradigm Simulation Using The Virtual Brain

## Abstract

The objective of this project is to simulate the neuronal dynamics of an auditory discrimination paradigm designed for the macaque cortex. This is achieved by performing whole-brain scale simulations employing The Virtual Brain (TVB) [1].

TVB is a computational framework that models neuronal populations at nodes, defines neuronal connections through a connectivity layer, and determines the pathway of information flow through neuronal pipelines.

For each node, an Adaptive Exponential (AdEx) neuronal population model is used. The connectivity layer is defined by the openly accessible CoCoMac Connectivity dataset [2], which is a matrix containing connection weights obtained from a macaque brain via diffusion MRI.

Cognitive tasks primarily involve the prefrontal cortex (PFC). In our auditory discrimination task, the pipeline starts from A1, which is stimulated by the auditory signals. This is then modulated in the PFC so that stimulus discrimination occurs. It concludes in the primary motor cortex (M1), which outputs the neuronal activity determining the motor action.

The aim of this study is to computationally contribute to the experimental investigation of cognitive dynamics of the macaque brain in auditory discrimination tasks. The outcomes of this study may shed light on the neural dynamics involved in decision-making.

## References

1. P. Sanz Leon, S. A. Knock, M. M. Woodman, L. Domide, J. Mersmann, A. R. McIntosh, and V. Jirsa, [“The virtual brain: a simulator of primate brain network dynamics,”](https://www.frontiersin.org/articles/10.3389/fninf.2013.00010/full) Frontiers in neuroinformatics, vol. 7, p. 10, 2013.
2. R. Bakker, T. Wachtler, and M. Diesmann, [“Cocomac 2.0 and the future of tract-tracing databases,”](https://www.frontiersin.org/articles/10.3389/fninf.2012.00030/full) Frontiers in neuroinformatics, vol. 6, p. 30, 2012.

