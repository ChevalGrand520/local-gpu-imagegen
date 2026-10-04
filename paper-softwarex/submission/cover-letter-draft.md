Dear Editors of SoftwareX,

Please consider my manuscript, “Local GPU Imagegen: Durable run records for local image generation,” as an Original Software Publication in SoftwareX.

Local GPU Imagegen is an open-source Python control plane that connects Model Context Protocol clients to local image-generation backends. It combines durable run records, explicit backend and workflow selection, and a guard for an earlier submission whose outcome is unknown. The manuscript describes the software architecture, installation and inspection interfaces, and the distinction between reading local run state and recovering a known backend job.

Six fixed paired Windows operations with ComfyUI illustrate the submission contract. After accepted response loss, the guarded path retains one accepted job while withholding another submission, but leaves the original client operation incomplete. A pre-send failure also produces a false block. These examples make the completion cost visible. They establish neither a new recovery policy nor improved general reliability, image quality or measured GPU savings; a synthetic simple-stop control matches the reported guard outcomes.

A separate CPU walkthrough demonstrates recovery with a retained job identifier: the engine records a generated round, while an independent adapter fixture reads history and image output without another prompt submission. These are synthetic component checks, not a new Windows or GPU experiment.

The manuscript fits SoftwareX's focus on research software and its application by presenting an inspectable local control plane with concrete source-based examples. The public MIT-licensed source snapshot contains installation documentation, the product implementation and separate research scripts. Derived records can be checked without a GPU; the original paired raw captures remain private and are explicitly unavailable for third-party recomputation. External adoption and downstream scientific impact have not been measured. The software snapshot and later manuscript-validation materials are identified separately through immutable GitHub links.

The work has not been published, posted as a preprint, or submitted for consideration elsewhere. The retained DSN and IEEE Access versions are internal drafts. The research received no specific funding and was completed by the sole author.

The author declares no competing financial interests or personal relationships that could have appeared to influence this work. The study did not involve human participants, identifiable personal data, or animal experiments. The author confirms lawful use of the software, diagrams and experimental materials.

[AUTHOR_INPUT_NEEDED: Review and approve the updated final manuscript and the selected submission materials before filing.]

Thank you for considering the manuscript.

Sincerely,

Zhen Cheng
School of Computer Science and Technology (School of Artificial Intelligence)
Zhejiang Sci-Tech University, Hangzhou, China
ChengZhen0105@outlook.com
