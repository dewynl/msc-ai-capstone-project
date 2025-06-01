# Unit 3: Project Types and Research Methods

# Types of Projects

When you are considering a computing project there are, broadly speaking, three different routes that you could take in terms of the type of the project available to you.

### Software Development

The first is a very traditional view of a computing project, in that you develop a piece of software to solve a particular problem. This type of project will require you to fully appreciate the problem space and develop a list of requirements that you will need to fulfil to successfully deliver your software. Next you will design the solution that you intend to develop before you begin to start work on developing your software. Finally, you will test and evaluate the success of your software and how well it met your initial requirements and design. This testing could take the form of performance testing, user testing or any other appropriate methods.

### Empirical Research

The second type of project you might consider is a project that carries out empirical research, this means that you will be collecting data yourself. Again, your project will still contain all of the fundamental aspects that we have previously discussed. You will carry out analysis work to understand what you are trying to achieve and what questions you are trying to answer. Next, you will design a means of collecting your data, which could be using a piece of software that you have created, and finally, you will analyze the data to draw the appropriate conclusions.

### Analytical Project

Finally, you may opt to carry out a project that is focused on the analytical aspects of computing.  This would mean potentially analyzing and understanding data that already exists. This does not mean that you would simply repeat what someone has already done.  Instead, in this type of project, you would be aiming to use the existing data in a novel way, to draw new comparisons, or apply the data in new ways. Again, as previously discussed, this project would see you develop the research questions you wish to answer during your analysis phase, design your data collection and analysis methods, and finally analyze the data to draw your new conclusions.

It is important to point out at this stage that it is entirely possible that you may use a number of different approaches in your project. For example, you may end up writing your own analysis software when using an empirical research approach.

# Software Development

First of all let’s take a look at what a typical software development project could look like with an example specification. In this example, we are going to consider an electronic attendance register for student attendance at their lectures.

Currently, student attendance is recorded using a simple paper sign-in sheet, which is handed out at the start of each lecture. This approach, while simple, suffers from a number of problems. Firstly, it is susceptible to being exploited by students that were not even at the lecture. Secondly, it is easy for students to miss the sheet and be marked as absent even when they are there!

An automated system, which allows students to sign in on their mobile devices would help to eliminate these problems and make it much easier to analyze attendance data.

With a project such as this it is clear that your project is going to be reliant on developing a prototype electronic sign-in system. How you approach this problem will very much depend on your own background research and experiences but in order to fulfil the problem brief you are going to need to write some software.

If you were to tackle a project such as this then the software that you develop would be the artefact that you have created.

The initial analysis would revolve around understanding existing systems and the state of the art, identifying potential platforms to develop your solution and understanding the main aim and objectives of this system. You would then move on to designing the architecture and system design, potentially using things like UML diagrams and other related techniques. When it comes to testing and validation it is possible to consider user-focused testing to see how well your product would satisfy its users whether this is students in the classroom or staff who would be using the system for analysis. You could also focus on performance testing to get an idea of how well the system might perform under pressure or its maximum capacity.

# Empirical Research

### **Empirical Research will focus on collecting your own data.**

This could be generating data with the software that you have developed, for instance the previous example of an electronic sign-in system could see you record network/performance data to understand how well the software performs, or this could be observing something or someone and recording those observations.

The example here is focused on keystroke dynamics and will involve observing people’s behaviors directly.

The specification states:

- Keystroke dynamics is the process of identifying an individual by the way that they type. Analyzing the timings of various key presses can be as uniquely identifiable as a fingerprint.
- In this project, you should aim to devise an experiment to determine a user’s identity based solely on the way that they type.

In this project, you would first need to research the existing approaches to keystroke dynamics and user identification in the current literature and use this to scope out the experiment that you wish to perform. This could take the form of creating a data collection platform and deploying it for your participants to use.

For example, a web page that requires users to copy a paragraph of text, while you record the timings of each keystroke. This will provide a research data set for analysis, which would form the testing and evaluation phase of your project, potentially using machine learning methods or more simple statistical analysis.

# Analytical Project

An analytical project will focus on interpreting data to draw potentially new conclusions or investigate new areas.

While typically projects will generate their own data, as an empirical study, it is entirely possible you may wish to use existing datasets and place your attention firmly on the analysis and investigation of the data.

If we take the previous example of keystroke dynamics, it is easy to see how this project could be recontextualized as an analytical project:

- Keystroke dynamics is a field that uses the cadence and rhythm of a user’s key presses to identify them. In addition to this, there is a range of other identity data that could potentially be discovered, for example, age, gender or handedness.
- In this project, you should devise analysis methods to investigate this potentially new identity data.

There is a wealth of datasets available for research online at sources such as Kaggle or Driven Data. Additionally, it is increasingly common for datasets to be published alongside academic papers to allow you to recreate the results or test new hypotheses.

**Again, as with the previous two project types you will still need to perform understanding the:**

1. **Requirements**: Aim to understand the current state of the art and develop your research question.
2. **Design**: Design your data processing pipeline, incorporating any data gathering, preparation to get things into a workable format, the design of your approach to data analysis and the methods you might use.
3. **Evaluation**: You are likely to place the biggest emphasis on the analysis and evaluation phase as you look to draw correlations or gain new insight into the data.

# Quantitative vs Qualitative

The type of research that you carry out, whether that’s qualitative or quantitative, will determine the methods and designs that are available to you. Whether you choose to use a qualitative approach or a quantitative approach will largely be governed by the question that you are trying to answer, as well as your own skills, experience and knowledge.

## Quantitative

At its simplest quantitative data can be thought of as dealing with numbers or statistics, we are thinking about things that can be assigned a quantity and that are measurable.

Often quantitative data will be expressed in terms of numbers or graphs, and it is used to confirm or test a theory or hypothesis.

When you undertake quantitative research, you are producing some generalizable facts about a given topic. For example, imagine analyzing fitness tracking data to understand the impact of regular exercise on overall fitness. You might look to record heart rate data over a period of time and look for correlations between an increase in the volume of exercise and its links to a lower resting heart rate. In order to establish this assertion, you would potentially use a graph to view the change of these two variables.

## Qualitative

In contrast to quantitative research’s focus on numbers and facts, qualitative research deals with words and meanings.

Qualitative research is usually expressed in words and used to describe thoughts, feeling and experiences. The aim of this research is to gain a deeper insight into topics that might not be well understood.

If we go back to our previous example of fitness tracking instead of looking at the measurable change that increased exercise may or may not bring, instead you might conduct a series of interviews to understand how doing more exercise makes them feel.

# **Comparing Quantitative and Qualitative**

As we have covered there are a number of contrasting differences in the two approaches.

Firstly, the two different approaches have different aims, with quantitative research aiming to test an existing hypothesis and assumption whereas qualitative research aims to further explore an idea and ultimately use that to develop a hypothesis.

As we have previously discussed, one of the main differences are the analysis that the methods use. Quantitative research uses statistical and numeric methods, whereas in contrast qualitative research will analyze the data to define categories. This relates to the type of data used to express the research, where quantitative research will use facts, figures and graphs whereas qualitative data is normally expressed with words and perceptions.

Quantitative research will typically aim to collect a large volume of data from a range of participants; this is because the aim to produce a generalized hypothesis and data collection methods are often not time consuming for the researcher. Qualitative research will normally need a smaller number of participants, because a greater volume of data is collected from each participant. We will discuss the different research methods that are used by both quantitative and qualitative.

| Quantitative | Qualitative |
| --- | --- |
| Aims to test a hypothesis. | Aims to explore ideas and potentially develop a theory. |
| Analysis typically uses statistical methods. | Analysis typically uses categorisation and summation. |
| Expressed using numbers and graphs. | Expressed in words. |
| Typically uses large samples of data. | Typically uses smaller samples of data. |
| Relies on closed questioning. | Relies on open questioning. |

# Quantitative Collection Methods

## Surveys

One of the key things to consider when choosing which method you are going to use to collect your data is: which method is going to help you to answer your research question?

There are a range of methods that are available to you, some of which will work with a qualitative approach, some of which will work with a quantitative approach and then some that can be used to collect either type of data.

A survey or questionnaire uses a series of questions to collect data, from a sample of the population.

The collected data can then be analyzed to identify trends and correlations. This type of data collection is something that should be familiar to the majority of you, as it is commonly used in assessing customer satisfaction or providing feedback to others. They offer a flexible method of data collection that can be applied to a wide range of projects.

### **Four Steps for a Successful Survey**

- **Determine**: Who will participate in the survey
- **Design**: The survey questions
- **Distribute**: The survey
- **Analyze**: the data

### 1. Determine who will participate in the survey

First of all, you need to determine who is going to take part in the survey, this could be a particular demographic such as a certain age group, or it could be individuals who have experience in certain areas. For example, you might be looking to gain insight from students aged 18 to 30 or you might be interested in people with previous software development experience.

### 2. Design the Survey Questions

Next you will need to think about how you will design your survey, this will consider the types of questions that you will use, how you will word them and the order that they will be presented in.

When considering quantitative research, you will predominantly use closed questioning (more on open questions later). Closed questions present your participant with a question followed by a number of predetermined responses.

There are a number of different types of closed questions where you give your participants a set of predetermined responses. This makes data analysis far easier as you will be performing a largely statistical analysis of the data.

First there is a Likert scale, which is typically 5 points where you gauge opinion or perception on a sliding scale. These types of question are particularly popular as they allow the responses to be tailored to the needs of the project and the researcher. In this example the responses range from strongly disagree to strongly agree.

Binary questions give your participants a simple choice between two options and while this is typically yes/no questions binary questions are not limited to these responses alone.

Finally, participants can be offered a list of options to choose from. This can be either something where a single option is appropriate such as their age or it could allow for multiple selections, for example, if you were conducting a survey around commonly used social media platforms you might ask a participant to select all of the networks these use.

When designing your survey, the content of the questions and how you phrase them is very important.

When you ask a question, you need to really consider why you are asking the question, and how is the information relevant to the overall research aims. Generally, it is a good rule to only ask questions where the response is relevant to your project, it is best to not collect data ’just in case you need it’.

The way that you phrase the question is equally important to the information that you are collecting. It is essential to ask in a clear and concise manner, but ensure you tailor the question to suit your target audience. For example, if you wanted to gauge perceptions about technology with a group of non-experts then you should aim to use clear, jargon free language. Whereas if you were surveying security professionals about their perceptions of upcoming risks then you would need to use appropriately technical language.

Lastly, ensure that you use neutral language in your questioning so that you do not bias the participants in any way. For example, if you were looking to determine general perceptions of the internet, if you asked the participants to ‘select the most significant dangers online’ then you risk a negative outlook from the start.

### 3. Distribute the Survey

When you start designing your research then it is important to consider things like who you are targeting in terms of participants and how many responses you might require.

When considering the sample size that you need there are a few different methods that are suitable for calculating a representative sample. For more information see Chapter 7 of Naked Statistics (Wheelan, 2013).

Next, you will need to think about who you are targeting as participants, whether that is a certain demographic, for example, age or gender, or those with certain experiences, for example, students.

**When recruiting participants there are several different ways to advertise your research.**

- **To friends, family and colleagues:** In the first instance, you can use your own networks, whether they are personal or professional, such as your friends, family and colleagues. However, this poses questions around whether the sample can be considered representative, particularly as we tend to associate with people who have things in common with ourselves.
- **Social media**: Social media presents an easy way to distribute your research to a wider, larger audience, but again you will need to be mindful of the self-selecting nature of your contacts and how this could impact how representative your sample really is.
- **Specialist participant recruitment websites:** There are websites that offer a means of promoting research studies, for example, Prolific and Mechanical Turk recruits participants in exchange for a fee. Reddit offers a number of subreddits specifically designed to allow users to advertise their research studies, Sample Size is one of the more popular subreddits.

### 4. Analyze the data

There are many different methods for analyzing the data that you have collected as part of the survey, although in the case of quantitative research and closed questions then you will most likely use statistical analysis to better understand your data. This will usually still be done using some software to support the analysis whether that is SPSS, Excel, Python or something else.

### Experiments

An experiment is a research method where you manipulate one or more independent variables and measure their effect on one or more dependent variables.

A well-designed experiment will test the validity of a hypothesis through a set of procedures or structured activities.

When you are designing an experiment, the aim is to study the effect of one variable on another, you are looking to establish cause and effect.

**In this case, the independent variable is the cause, and the dependent variable is the effect.**

To give an example, if we were investigating social media usage and its impact on the sleep of users then the:

- **Independent Variable**: would be the amount of social media usage.
- **Dependent Variable**: The quality or amount of sleep would act as the dependent variable.

---

# Qualitative Collection Methods

## **Interviews and Focus Groups**

Let’s now take a look at some examples of qualitative data collection methods, specifically:

- Interviews
- Focus Group
- Ethnography
- Literature Review

### Interviews

Interviews are similar to surveys in that you are defining a list of questions to ask your participants. However, whereas a survey is a passive approach, maybe a website or sheet of paper, an interview will typically require you to talk to someone directly. You may use some closed questions, but in reality, the focus of an interview will usually be open questions which have no predetermined answers and allow the participants to express themselves in their own words. The same guidelines apply to both surveys and interviews in that you should aim to pose questions neutrally and not lead your participants. The key difference is that your analysis will be focused on drawing out themes and trends in the qualitative data, using methods such as thematic analysis.

### Focus Group

A similar approach to an interview, with a group of people to gather opinions about a topic that can be used for further research.

## **Ethnography and Literature Reviews**

### Ethnography

Ethnography is a research method that involves immersing yourself in a particular community or organization to observe behaviors and interactions up close.

This is considered to be a really flexible research method that allows you to gain a deeper insight and understanding into a group’s culture, conventions and dynamics.

As an example, if you were interested in the proliferation of DevSecOps and its impact on software development then you might look to be based with a development team to observe their practices and how they compare with other similar teams like a simple DevOps team.

### Literature Review

A literature review is a survey of existing sources, usually academic, on a specific topic.

Your aim is to provide an overview of the current knowledge and thinking on a subject and highlight any gaps in the research.

Using a literature review approach to a project is by no means the easy option, you are not simply summarizing what is there but instead analyzing and critically evaluating the existing knowledge.