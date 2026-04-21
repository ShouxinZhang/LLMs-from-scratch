## CELL 0
<table style="width:100%">
<tr>
<td style="vertical-align:middle; text-align:left;">
<font size="2">
Supplementary code for the <a href="http://mng.bz/orYv">Build a Large Language Model From Scratch</a> book by <a href="https://sebastianraschka.com">Sebastian Raschka</a><br>
<br>Code repository: <a href="https://github.com/rasbt/LLMs-from-scratch">https://github.com/rasbt/LLMs-from-scratch</a>
</font>
</td>
<td style="vertical-align:middle; text-align:left;">
<a href="http://mng.bz/orYv"><img src="https://sebastianraschka.com/images/LLMs-from-scratch-images/cover-small.webp" width="100px"></a>
</td>
</tr>
</table>

## CELL 1
# Chapter 3: Coding Attention Mechanisms

## CELL 2
Packages that are being used in this notebook:

## CELL 4
- This chapter covers attention mechanisms, the engine of LLMs:

## CELL 5
<img src="https://sebastianraschka.com/images/LLMs-from-scratch-images/ch03_compressed/01.webp?123" width="500px">

## CELL 6
<img src="https://sebastianraschka.com/images/LLMs-from-scratch-images/ch03_compressed/02.webp" width="600px">

## CELL 7
&nbsp;
## 3.1 The problem with modeling long sequences

## CELL 8
- No code in this section
- Translating a text word by word isn't feasible due to the differences in grammatical structures between the source and target languages:

## CELL 9
<img src="https://sebastianraschka.com/images/LLMs-from-scratch-images/ch03_compressed/03.webp" width="400px">

## CELL 10
- Prior to the introduction of transformer models, encoder-decoder RNNs were commonly used for machine translation tasks
- In this setup, the encoder processes a sequence of tokens from the source language, using a hidden state—a kind of intermediate layer within the neural network—to generate a condensed representation of the entire input sequence:

## CELL 11
<img src="https://sebastianraschka.com/images/LLMs-from-scratch-images/ch03_compressed/04.webp" width="500px">

## CELL 12
&nbsp;
## 3.2 Capturing data dependencies with attention mechanisms

## CELL 13
- No code in this section
- Through an attention mechanism, the text-generating decoder segment of the network is capable of selectively accessing all input tokens, implying that certain input tokens hold more significance than others in the generation of a specific output token:

## CELL 14
<img src="https://sebastianraschka.com/images/LLMs-from-scratch-images/ch03_compressed/05.webp" width="500px">

## CELL 15
- Self-attention in transformers is a technique designed to enhance input representations by enabling each position in a sequence to engage with and determine the relevance of every other position within the same sequence

## CELL 16
<img src="https://sebastianraschka.com/images/LLMs-from-scratch-images/ch03_compressed/06.webp" width="300px">

## CELL 17
&nbsp;
## 3.3 Attending to different parts of the input with self-attention

## CELL 18
&nbsp;
### 3.3.1 A simple self-attention mechanism without trainable weights

## CELL 19
- This section explains a very simplified variant of self-attention, which does not contain any trainable weights
- This is purely for illustration purposes and NOT the attention mechanism that is used in transformers
- The next section, section 3.3.2, will extend this simple attention mechanism to implement the real self-attention mechanism
- Suppose we are given an input sequence $x^{(1)}$ to $x^{(T)}$
  - The input is a text (for example, a sentence like "Your journey starts with one step") that has already been converted into token embeddings as described in chapter 2
  - For instance, $x^{(1)}$ is a d-dimensional vector representing the word "Your", and so forth
- **Goal:** compute context vectors $z^{(i)}$ for each input sequence element $x^{(i)}$ in $x^{(1)}$ to $x^{(T)}$ (where $z$ and $x$ have the same dimension)
    - A context vector $z^{(i)}$ is a weighted sum over the inputs $x^{(1)}$ to $x^{(T)}$
    - The context vector is "context"-specific to a certain input
      - Instead of $x^{(i)}$ as a placeholder for an arbitrary input token, let's consider the second input, $x^{(2)}$
      - And to continue with a concrete example, instead of the placeholder $z^{(i)}$, we consider the second output context vector, $z^{(2)}$
      - The second context vector, $z^{(2)}$, is a weighted sum over all inputs $x^{(1)}$ to $x^{(T)}$ weighted with respect to the second input element, $x^{(2)}$
      - The attention weights are the weights that determine how much each of the input elements contributes to the weighted sum when computing $z^{(2)}$
      - In short, think of $z^{(2)}$ as a modified version of $x^{(2)}$ that also incorporates information about all other input elements that are relevant to a given task at hand

## CELL 20
<img src="https://sebastianraschka.com/images/LLMs-from-scratch-images/ch03_compressed/07.webp" width="400px">

- (Please note that the numbers in this figure are truncated to one
digit after the decimal point to reduce visual clutter; similarly, other figures may also contain truncated values)

## CELL 21
- By convention, the unnormalized attention weights are referred to as **"attention scores"** whereas the normalized attention scores, which sum to 1, are referred to as **"attention weights"**

## CELL 22
- The code below walks through the figure above step by step

<br>

- **Step 1:** compute unnormalized attention scores $\omega$
- Suppose we use the second input token as the query, that is, $q^{(2)} = x^{(2)}$, we compute the unnormalized attention scores via dot products:
    - $\omega_{21} = x^{(1)} q^{(2)\top}$
    - $\omega_{22} = x^{(2)} q^{(2)\top}$
    - $\omega_{23} = x^{(3)} q^{(2)\top}$
    - ...
    - $\omega_{2T} = x^{(T)} q^{(2)\top}$
- Above, $\omega$ is the Greek letter "omega" used to symbolize the unnormalized attention scores
    - The subscript "21" in $\omega_{21}$ means that input sequence element 2 was used as a query against input sequence element 1

## CELL 23
- Suppose we have the following input sentence that is already embedded in 3-dimensional vectors as described in chapter 3 (we use a very small embedding dimension here for illustration purposes, so that it fits onto the page without line breaks):

## CELL 25
- (In this book, we follow the common machine learning and deep learning convention where training examples are represented as rows and feature values as columns; in the case of the tensor shown above, each row represents a word, and each column represents an embedding dimension)

- The primary objective of this section is to demonstrate how the context vector $z^{(2)}$
  is calculated using the second input sequence, $x^{(2)}$, as a query

- The figure depicts the initial step in this process, which involves calculating the attention scores ω between $x^{(2)}$
  and all other input elements through a dot product operation

## CELL 26
<img src="https://sebastianraschka.com/images/LLMs-from-scratch-images/ch03_compressed/08.webp" width="400px">

## CELL 27
- We use input sequence element 2, $x^{(2)}$, as an example to compute context vector $z^{(2)}$; later in this section, we will generalize this to compute all context vectors.
- The first step is to compute the unnormalized attention scores by computing the dot product between the query $x^{(2)}$ and all other input tokens:

## CELL 29
- Side note: a dot product is essentially a shorthand for multiplying two vectors elements-wise and summing the resulting products:

## CELL 31
- **Step 2:** normalize the unnormalized attention scores ("omegas", $\omega$) so that they sum up to 1
- Here is a simple way to normalize the unnormalized attention scores to sum up to 1 (a convention, useful for interpretation, and important for training stability):

## CELL 32
<img src="https://sebastianraschka.com/images/LLMs-from-scratch-images/ch03_compressed/09.webp" width="500px">

## CELL 34
- However, in practice, using the softmax function for normalization, which is better at handling extreme values and has more desirable gradient properties during training, is common and recommended.
- Here's a naive implementation of a softmax function for scaling, which also normalizes the vector elements such that they sum up to 1:

## CELL 36
- The naive implementation above can suffer from numerical instability issues for large or small input values due to overflow and underflow issues
- Hence, in practice, it's recommended to use the PyTorch implementation of softmax instead, which has been highly optimized for performance:

## CELL 38
- **Step 3**: compute the context vector $z^{(2)}$ by multiplying the embedded input tokens, $x^{(i)}$ with the attention weights and sum the resulting vectors:

## CELL 39
<img src="https://sebastianraschka.com/images/LLMs-from-scratch-images/ch03_compressed/10.webp" width="500px">

## CELL 41
&nbsp;
### 3.3.2 Computing attention weights for all input tokens

## CELL 42
#### Generalize to all input sequence tokens:

- Above, we computed the attention weights and context vector for input 2 (as illustrated in the highlighted row in the figure below)
- Next, we are generalizing this computation to compute all attention weights and context vectors

## CELL 43
<img src="https://sebastianraschka.com/images/LLMs-from-scratch-images/ch03_compressed/11.webp" width="400px">

- (Please note that the numbers in this figure are truncated to two
digits after the decimal point to reduce visual clutter; the values in each row should add up to 1.0 or 100%; similarly, digits in other figures are truncated)

## CELL 44
- In self-attention, the process starts with the calculation of attention scores, which are subsequently normalized to derive attention weights that total 1
- These attention weights are then utilized to generate the context vectors through a weighted summation of the inputs

## CELL 45
<img src="https://sebastianraschka.com/images/LLMs-from-scratch-images/ch03_compressed/12.webp" width="400px">

## CELL 46
- Apply previous **step 1** to all pairwise elements to compute the unnormalized attention score matrix:

## CELL 48
- We can achieve the same as above more efficiently via matrix multiplication:

## CELL 50
- Similar to **step 2** previously, we normalize each row so that the values in each row sum to 1:

## CELL 52
- Quick verification that the values in each row indeed sum to 1:

## CELL 54
- Apply previous **step 3** to compute all context vectors:

## CELL 56
- As a sanity check, the previously computed context vector $z^{(2)} = [0.4419, 0.6515, 0.5683]$ can be found in the 2nd row in above:

## CELL 58
&nbsp;
## 3.4 Implementing self-attention with trainable weights

## CELL 59
- A conceptual framework illustrating how the self-attention mechanism developed in this section integrates into the overall narrative and structure of this book and chapter

## CELL 60
<img src="https://sebastianraschka.com/images/LLMs-from-scratch-images/ch03_compressed/13.webp" width="400px">

## CELL 61
&nbsp;
### 3.4.1 Computing the attention weights step by step

## CELL 62
- In this section, we are implementing the self-attention mechanism that is used in the original transformer architecture, the GPT models, and most other popular LLMs
- This self-attention mechanism is also called "scaled dot-product attention"
- The overall idea is similar to before:
  - We want to compute context vectors as weighted sums over the input vectors specific to a certain input element
  - For the above, we need attention weights
- As you will see, there are only slight differences compared to the basic attention mechanism introduced earlier:
  - The most notable difference is the introduction of weight matrices that are updated during model training
  - These trainable weight matrices are crucial so that the model (specifically, the attention module inside the model) can learn to produce "good" context vectors

## CELL 63
<img src="https://sebastianraschka.com/images/LLMs-from-scratch-images/ch03_compressed/14.webp" width="600px">

## CELL 64
- Implementing the self-attention mechanism step by step, we will start by introducing the three training weight matrices $W_q$, $W_k$, and $W_v$
- These three matrices are used to project the embedded input tokens, $x^{(i)}$, into query, key, and value vectors via matrix multiplication:

  - Query vector: $q^{(i)} = x^{(i)}\,W_q $
  - Key vector: $k^{(i)} = x^{(i)}\,W_k $
  - Value vector: $v^{(i)} = x^{(i)}\,W_v $

## CELL 65
- The embedding dimensions of the input $x$ and the query vector $q$ can be the same or different, depending on the model's design and specific implementation
- In GPT models, the input and output dimensions are usually the same, but for illustration purposes, to better follow the computation, we choose different input and output dimensions here:

## CELL 67
- Below, we initialize the three weight matrices; note that we are setting `requires_grad=False` to reduce clutter in the outputs for illustration purposes, but if we were to use the weight matrices for model training, we would set `requires_grad=True` to update these matrices during model training

## CELL 69
- Next we compute the query, key, and value vectors:

## CELL 71
- As we can see below, we successfully projected the 6 input tokens from a 3D onto a 2D embedding space:

## CELL 73
- In the next step, **step 2**, we compute the unnormalized attention scores by computing the dot product between the query and each key vector:

## CELL 74
<img src="https://sebastianraschka.com/images/LLMs-from-scratch-images/ch03_compressed/15.webp" width="600px">

## CELL 76
- Since we have 6 inputs, we have 6 attention scores for the given query vector:

## CELL 78
<img src="https://sebastianraschka.com/images/LLMs-from-scratch-images/ch03_compressed/16.webp" width="600px">

## CELL 79
- Next, in **step 3**, we compute the attention weights (normalized attention scores that sum up to 1) using the softmax function we used earlier
- The difference to earlier is that we now scale the attention scores by dividing them by the square root of the embedding dimension, $\sqrt{d_k}$ (i.e., `d_k**0.5`):

## CELL 81
<img src="https://sebastianraschka.com/images/LLMs-from-scratch-images/ch03_compressed/17.webp" width="600px">

## CELL 82
- In **step 4**, we now compute the context vector for input query vector 2:

## CELL 84
&nbsp;
### 3.4.2 Implementing a compact SelfAttention class

## CELL 85
- Putting it all together, we can implement the self-attention mechanism as follows:

## CELL 87
<img src="https://sebastianraschka.com/images/LLMs-from-scratch-images/ch03_compressed/18.webp" width="400px">

## CELL 88
- We can streamline the implementation above using PyTorch's Linear layers, which are equivalent to a matrix multiplication if we disable the bias units
- Another big advantage of using `nn.Linear` over our manual `nn.Parameter(torch.rand(...)` approach is that `nn.Linear` has a preferred weight initialization scheme, which leads to more stable model training

## CELL 90
- Note that `SelfAttention_v1` and `SelfAttention_v2` give different outputs because they use different initial weights for the weight matrices

## CELL 91
&nbsp;
## 3.5 Hiding future words with causal attention

## CELL 92
- In causal attention, the attention weights above the diagonal are masked, ensuring that for any given input, the LLM is unable to utilize future tokens while calculating the context vectors with the attention weight

## CELL 93
<img src="https://sebastianraschka.com/images/LLMs-from-scratch-images/ch03_compressed/19.webp" width="400px">

## CELL 94
&nbsp;
### 3.5.1 Applying a causal attention mask

## CELL 95
- In this section, we are converting the previous self-attention mechanism into a causal self-attention mechanism
- Causal self-attention ensures that the model's prediction for a certain position in a sequence is only dependent on the known outputs at previous positions, not on future positions
- In simpler words, this ensures that each next word prediction should only depend on the preceding words
- To achieve this, for each given token, we mask out the future tokens (the ones that come after the current token in the input text):

## CELL 96
<img src="https://sebastianraschka.com/images/LLMs-from-scratch-images/ch03_compressed/20.webp" width="600px">

## CELL 97
- To illustrate and implement causal self-attention, let's work with the attention scores and weights from the previous section:

## CELL 99
- The simplest way to mask out future attention weights is by creating a mask via PyTorch's tril function with elements below the main diagonal (including the diagonal itself) set to 1 and above the main diagonal set to 0:

## CELL 101
- Then, we can multiply the attention weights with this mask to zero out the attention scores above the diagonal:

## CELL 103
- However, if the mask were applied after softmax, like above, it would disrupt the probability distribution created by softmax
- Softmax ensures that all output values sum to 1
- Masking after softmax would require re-normalizing the outputs to sum to 1 again, which complicates the process and might lead to unintended effects

## CELL 104
- To make sure that the rows sum to 1, we can normalize the attention weights as follows:

## CELL 106
- While we are technically done with coding the causal attention mechanism now, let's briefly look at a more efficient approach to achieve the same as above
- So, instead of zeroing out attention weights above the diagonal and renormalizing the results, we can mask the unnormalized attention scores above the diagonal with negative infinity before they enter the softmax function:

## CELL 107
<img src="https://sebastianraschka.com/images/LLMs-from-scratch-images/ch03_compressed/21.webp" width="450px">

## CELL 109
- As we can see below, now the attention weights in each row correctly sum to 1 again:

## CELL 111
&nbsp;
### 3.5.2 Masking additional attention weights with dropout

## CELL 112
- In addition, we also apply dropout to reduce overfitting during training
- Dropout can be applied in several places:
  - for example, after computing the attention weights;
  - or after multiplying the attention weights with the value vectors
- Here, we will apply the dropout mask after computing the attention weights because it's more common

- Furthermore, in this specific example, we use a dropout rate of 50%, which means randomly masking out half of the attention weights. (When we train the GPT model later, we will use a lower dropout rate, such as 0.1 or 0.2

## CELL 113
<img src="https://sebastianraschka.com/images/LLMs-from-scratch-images/ch03_compressed/22.webp" width="400px">

## CELL 114
- If we apply a dropout rate of 0.5 (50%), the non-dropped values will be scaled accordingly by a factor of 1/0.5 = 2
- The scaling is calculated by the formula 1 / (1 - `dropout_rate`)

## CELL 117
- Note that the resulting dropout outputs may look different depending on your operating system; you can read more about this inconsistency [here on the PyTorch issue tracker](https://github.com/pytorch/pytorch/issues/121595)

## CELL 118
&nbsp;
### 3.5.3 Implementing a compact causal self-attention class

## CELL 119
- Now, we are ready to implement a working implementation of self-attention, including the causal and dropout masks
- One more thing is to implement the code to handle batches consisting of more than one input so that our `CausalAttention` class supports the batch outputs produced by the data loader we implemented in chapter 2
- For simplicity, to simulate such batch input, we duplicate the input text example:

## CELL 122
- Note that dropout is only applied during training, not during inference

## CELL 123
<img src="https://sebastianraschka.com/images/LLMs-from-scratch-images/ch03_compressed/23.webp" width="500px">

## CELL 124
&nbsp;
## 3.6 Extending single-head attention to multi-head attention

## CELL 125
&nbsp;
### 3.6.1 Stacking multiple single-head attention layers

## CELL 126
- Below is a summary of the self-attention implemented previously (causal and dropout masks not shown for simplicity)

- This is also called single-head attention:

<img src="https://sebastianraschka.com/images/LLMs-from-scratch-images/ch03_compressed/24.webp" width="400px">

- We simply stack multiple single-head attention modules to obtain a multi-head attention module:

<img src="https://sebastianraschka.com/images/LLMs-from-scratch-images/ch03_compressed/25.webp" width="400px">

- The main idea behind multi-head attention is to run the attention mechanism multiple times (in parallel) with different, learned linear projections. This allows the model to jointly attend to information from different representation subspaces at different positions.

## CELL 128
- In the implementation above, the embedding dimension is 4, because we `d_out=2` as the embedding dimension for the key, query, and value vectors as well as the context vector. And since we have 2 attention heads, we have the output embedding dimension 2*2=4

## CELL 129
&nbsp;
### 3.6.2 Implementing multi-head attention with weight splits

## CELL 130
- While the above is an intuitive and fully functional implementation of multi-head attention (wrapping the single-head attention `CausalAttention` implementation from earlier), we can write a stand-alone class called `MultiHeadAttention` to achieve the same

- We don't concatenate single attention heads for this stand-alone `MultiHeadAttention` class
- Instead, we create single W_query, W_key, and W_value weight matrices and then split those into individual matrices for each attention head:

## CELL 132
- Note that the above is essentially a rewritten version of `MultiHeadAttentionWrapper` that is more efficient
- The resulting output looks a bit different since the random weight initializations differ, but both are fully functional implementations that can be used in the GPT class we will implement in the upcoming chapters

## CELL 133
---

**A note about the output dimensions**

- In the `MultiHeadAttention` above, I used `d_out=2` to use the same setting as in the `MultiHeadAttentionWrapper` class earlier
- The `MultiHeadAttentionWrapper`, due the the concatenation, returns the output head dimension `d_out * num_heads` (i.e., `2*2 = 4`)
- However, the `MultiHeadAttention` class (to make it more user-friendly) allows us to control the output head dimension directly via `d_out`; this means, if we set `d_out = 2`, the output head dimension will be 2, regardless of the number of heads
- In hindsight, as readers [pointed out](https://github.com/rasbt/LLMs-from-scratch/pull/859), it may be more intuitive to use `MultiHeadAttention` with `d_out = 4` so that it produces the same output dimensions as `MultiHeadAttentionWrapper` with `d_out = 2`.

---

## CELL 134
- Note that in addition, we added a linear projection layer (`self.out_proj `) to the `MultiHeadAttention` class above. This is simply a linear transformation that doesn't change the dimensions. It's a standard convention to use such a projection layer in LLM implementation, but it's not strictly necessary (recent research has shown that it can be removed without affecting the modeling performance; see the further reading section at the end of this chapter)

## CELL 135
<img src="https://sebastianraschka.com/images/LLMs-from-scratch-images/ch03_compressed/26.webp" width="400px">

## CELL 136
- Note that if you are interested in a compact and efficient implementation of the above, you can also consider the [`torch.nn.MultiheadAttention`](https://pytorch.org/docs/stable/generated/torch.nn.MultiheadAttention.html) class in PyTorch

## CELL 137
- Since the above implementation may look a bit complex at first glance, let's look at what happens when executing `attn_scores = queries @ keys.transpose(2, 3)`:

## CELL 139
- In this case, the matrix multiplication implementation in PyTorch will handle the 4-dimensional input tensor so that the matrix multiplication is carried out between the 2 last dimensions (num_tokens, head_dim) and then repeated for the individual heads 

- For instance, the following becomes a more compact way to compute the matrix multiplication for each head separately:

## CELL 141
&nbsp;
## Summary and takeaways

## CELL 142
- See the [./multihead-attention.ipynb](./multihead-attention.ipynb) code notebook, which is a concise version of the data loader (chapter 2) plus the multi-head attention class that we implemented in this chapter and will need for training the GPT model in upcoming chapters
- You can find the exercise solutions in [./exercise-solutions.ipynb](./exercise-solutions.ipynb)
