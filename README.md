# webvulmap

This is a web application maps between software security topics (CWEs and CVEs)
and CS curriculum topics. It serves two main goals:

1. it allows instructors or learners understand what prerequisite material is
	 needed to help teach/learn about certain secure programming topics in terms
	 of CWEs and CVEs, and
1. it also helps them locate real world examples, such as CWEs and CVEs
	 relevant to a course topic.

With this tool, one can learn what common language (i.e. c++, SQL) and
knowledge are associated with a known secure vulnerability (e.g., a CWE or a
CVE) and follows up with web sources to learn more. For instance, learners are
currently studying a topic in interested in their course, such as, Classic
Buffer Overflow (a Knowledge Topic). This tool can informs the learners that
this problem is commonly observed in programming languages like C/C++, and
secure vulnerabilities caused by this problem is often categorized as CWE-120
Classic Buffer Overflow. The tool links to CVE instances in this CWE, such as
CVE-2000-1094, i.e.,  a Buffer Overflow bug in AOL Instant Messenger (AIM)
before 4.3.2229 allows remote attackers to execute arbitrary commands via a
"buddyicon" command with a long "src" argument (source:
[https://nvd.nist.gov/vuln/detail/CVE-2000-1094](https://nvd.nist.gov/vuln/detail/CVE-2000-1094))
