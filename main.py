import ioh
from scipy.stats.qmc import scale, LatinHypercube as lhs, Sobol, Halton
from sklearn.svm import SVC
from modcma import Parameters, Population, ModularCMAES
from argparse import ArgumentParser
import numpy as np
from itertools import combinations
from typing import List


def initialize_parameters(
    problem: ioh.ProblemType,
    budget: int,
    lambda_: int,
    n_generations: int = None,
    x0: np.ndarray = None,
    sigma0: float = 0.2,
    initialization_correction: str = None,
    svm: SVC = None,
    subpopulation_target: str = None,
    area_coefs: np.ndarray = None,
    a_tpa: float = 0.5,
    b_tpa: float = 0.0,
    cs: float = None,
    cmu: float = None,
    c1: float = None,
    seq_cutoff_factor: int = 1,
    init_threshold: float = 0.2,
    decay_factor: float = 0.995,
    max_resamples: int = 1000,
    active: bool = False,
    elitist: bool = False,
    sequential: bool = False,
    threshold_convergence: bool = False,
    bound_correction: str = None,
    orthogonal: bool = False,
    local_restart: str = None,
    base_sampler: str = "gaussian",
    mirrored: str = "mirrored",
    weights_option: str = "default",
    step_size_adaptation: str = "csa",
    population: Population = None,
    old_population: Population = None,
    ipop_factor: int = 2,
    ps_factor: float = 1.0,
    sample_sigma: bool = False,
):
    CMAES_params = Parameters(
        d=problem.meta_data.n_variables,
        lambda_=lambda_,
        x0=x0,
        initialization_correction=initialization_correction,
        svm=svm,
        subpopulation_target=subpopulation_target,
        area_coefs=area_coefs,  # ub=problem.bounds.ub, lb=problem.bounds.lb,
        budget=budget,
        target=problem.optimum.y + abs(problem.optimum.y) * 10e-9,
        n_generations=n_generations,
        sigma0=sigma0,
        a_tpa=a_tpa,
        b_tpa=b_tpa,
        cs=cs,
        cmu=cmu,
        c1=c1,
        seq_cutoff_factor=seq_cutoff_factor,
        init_threshold=init_threshold,
        decay_factor=decay_factor,
        max_resamples=max_resamples,
        active=active,
        elitist=elitist,
        sequential=sequential,
        threshold_convergence=threshold_convergence,
        bound_correction=bound_correction,
        orthogonal=orthogonal,
        local_restart=local_restart,
        base_sampler=base_sampler,
        mirrored=mirrored,
        weights_option=weights_option,
        step_size_adaptation=step_size_adaptation,
        population=population,
        old_population=old_population,
        ipop_factor=ipop_factor,
        ps_factor=ps_factor,
        sample_sigma=sample_sigma,
    )
    return CMAES_params


def initialize_centroids(
    problem: ioh.ProblemType, sub_pop: int, init_method: str
) -> np.ndarray:
    if init_method == "uniform":
        return np.random.uniform(
            problem.bounds.lb,
            problem.bounds.ub,
            (
                sub_pop,
                problem.meta_data.n_variables,
            ),
        )
    elif init_method == "lhs":
        return np.float64(
            scale(
                lhs(d=problem.meta_data.n_variables).random(sub_pop),
                l_bounds=problem.bounds.lb,
                u_bounds=problem.bounds.ub,
            )
        )
    elif init_method == "sobol":
        return np.float64(
            scale(
                Sobol(d=problem.meta_data.n_variables).random(sub_pop),
                l_bounds=problem.bounds.lb,
                u_bounds=problem.bounds.ub,
            )
        )
    elif init_method == "halton":
        return np.float64(
            scale(
                Halton(d=problem.meta_data.n_variables).random(sub_pop),
                l_bounds=problem.bounds.lb,
                u_bounds=problem.bounds.ub,
            )
        )
    elif init_method == "gaussian":
        return np.random.randn(problem.meta_data.n_variables, sub_pop)
    elif init_method == "center":
        return np.zeros((sub_pop, problem.meta_data.n_variables))
    else:
        raise ValueError("Incorrect initialization technique.")


def extract_svm_coefs(svm: SVC, targets: List[str], target: str):
    if svm:
        return [
            (svm.coef_[i], svm.intercept_[i])
            for i, c in enumerate(combinations(targets, 2))
            if target in c
        ]
    else:
        return None


def initialize(
    problem_id: int,
    problem_instance: int,
    dimension: int,
    budget: int,
    iterations: int,
    lambda_: List[int],
    bound_corr: str,
    init_method: str,
    sigma0: float,
    init_corr: str,
    sharing: tuple,
    logger_info: dict,
):
    problem = ioh.get_problem(
        fid=problem_id,
        instance=problem_instance,
        dimension=dimension,
        problem_type=ioh.ProblemType.BBOB,
    )  # TODO replace dimension
    # print(problem)

    x0 = initialize_centroids(
        problem=problem, sub_pop=len(lambda_), init_method=init_method
    )

    svm = None
    labels = [None] * len(lambda_)
    if init_corr:
        labels = list(range(len(x0)))
        svm = SVC(kernel="linear").fit(x0, labels)

    x0 = x0.reshape((len(lambda_), problem.meta_data.n_variables, 1))

    logger = ioh.logger.Analyzer(
        root="data",
        folder_name="run",
        algorithm_name=logger_info["name"],
        algorithm_info="test of IOHexperimenter in python",
    )
    problem.attach_logger(logger)

    # initialize (subpop) number of populations
    subpop_n = len(lambda_)
    cmaes = []
    for i in range(subpop_n):
        params = initialize_parameters(
            problem=problem,
            budget=budget,
            lambda_=lambda_[i],
            x0=x0[i],
            sigma0=sigma0 if isinstance(sigma0, float) else sigma0[i],
            bound_correction=bound_corr,
            initialization_correction=init_corr,
            svm=svm,
            subpopulation_target=i,
            area_coefs=extract_svm_coefs(svm, labels, i),
        )
        cmaes.append(ModularCMAES(fitness_func=problem, parameters=params))

    return run_cma(
        CMAES=np.array(cmaes),
        iterations=iterations,
        corr=svm,
        sharing=sharing,
    )


def run_cma(
    CMAES: np.ndarray,
    iterations: int,
    corr: SVC,
    sharing: tuple,
):
    break_conditions = [None] * len(lambda_)

    for iter in range(iterations):
        if sharing is not None:
            t, r, *mode = sharing
            t, r = int(t), float(r)
            if iter != 0 and iter % t == 0:
                improvements = np.array([np.average(CMAES[n].parameters.calculate_improvement(low=iter-int(t), high=iter)) for n in range(len(CMAES))])
                CMAES = CMAES[improvements.argsort()]
                inc = max(int(2*np.floor((CMAES[-1].parameters.lambda_ * r)/2)), 2)
                if CMAES[-1].parameters.lambda_ - inc >= 2:
                    CMAES[0].parameters.update_popsize(CMAES[0].parameters.lambda_ + inc)
                    if len(mode) > 0 and mode[0] == 'ipop': CMAES[-1].parameters.update_popsize(CMAES[-1].parameters.lambda_ - inc)

        for i in range(len(CMAES)):
            if corr:
                CMAES[i].parameters.svm = corr
                CMAES[i].parameters.area_coefs = extract_svm_coefs(
                    corr, range(len(lambda_)), i
                )
            CMAES[i].step()
            break_conditions[i] = any(CMAES[i].break_conditions)

        if any(break_conditions):
            break

        if corr: 
            centroids = np.float64(
                [
                    CMAES[n].parameters.m.reshape((CMAES[i].parameters.d,))
                    for n in range(len(CMAES))
                ]
            )
            corr = SVC(kernel="linear").fit(centroids, range(len(lambda_)))
    return CMAES


def main(
    problem_id: int,
    problem_instance: int,
    dimension: int,
    iterations: int,
    budget: int,
    lambda_: int,
    bound_corr: str,
    init_method: str,
    sigma0: float,
    init_corr: str,
    sharing: tuple,
    logger_info: dict,
):
    # initialize
    cmaes = initialize(
        problem_id=problem_id,
        problem_instance=problem_instance,
        dimension=dimension,
        budget=budget,
        iterations=iterations,
        lambda_=lambda_,
        bound_corr=bound_corr,
        init_method=init_method,
        sigma0=sigma0,
        init_corr=init_corr,
        sharing=sharing,
        logger_info=logger_info,
    )

    # TODO fix run algo
    # cmaes = run_cma(CMAES=cmaes, iterations=iterations, sharing_point=sharing_point)

    # display results
    for cma in cmaes:
        print(
            f"CMA: {cma} f:{cma.parameters.fopt}, {cma._fitness_func.optimum.y}, {cma.parameters.population}"
        )


if __name__ == "__main__":
    # TODO: seed
    np.random.seed(7)
    parser = ArgumentParser()
    parser.add_argument(
        "-pid",
        "--problem_id",
        help="decide which BBOB problem to run CMAES on",
        choices=list(range(1, 25)),
        default=3,
        type=int,
    )  # only those two for now
    parser.add_argument(
        "-iid",
        "--problem_instance",
        help="decide which instance of the problem to run CMAES on",
        choices=list(range(1, 16)),
        default=1,
        type=int,
    )  # instances 1-15
    parser.add_argument(
        "-d",
        "--dimension",
        help="the dimension of the problem we are solving {2/5/20}",
        default=5,
        type=int,
    )
    parser.add_argument(
        "-i",
        "--iterations",
        help="how many iterations to run the algorithm for",
        default=10000,
        type=int,
    )  
    parser.add_argument(
        "-b",
        "--budget",
        help="decides the budget of the problem, defaults to 1e4*dimension",
        nargs="?",
        default=1e4,
        type=float,
    )
    parser.add_argument(
        "-pt",
        "--subpop_type",
        help="sizes of subpopulations",
        choices=[1, 2, 3, 4, 5],
        default=1,
        type=int,
    )
    parser.add_argument(
        "-im",
        "--init_method",
        help="",
        default="uniform",
        choices=["uniform", "lhs", "sobol", "halton", "gaussian", "center"],
        type=str,
    )
    parser.add_argument("-s", "--sigma0", help="", default=0.2, type=float)
    parser.add_argument("-bc", "--bound_corr", help="", default="saturate", type=str)
    parser.add_argument(
        "-ic",
        "--init_corr",
        help="Initialization correction {None, 'svm-i', 'svm-o'}",
        default=None,
        type=str,
    )
    parser.add_argument(
        "-n", "--algo_name", help="algorithm name", default="ModCMA", type=str
    )
    parser.add_argument(
        "-l",
        "--lambda_",
        help="size of offsprings to generate",
        default=100,
        type=int,
    )
    # parser.add_argument("-m", "--mu_", help="size of parents to use", nargs='*', default=100, type=int)
    # parser.add_argument("-p", "--subpop", help="size of subpopulation parents and offspring\neg: [100, 50, 20, 10, 5]", nargs='+', default=None, type=int)
    # parser.add_argument("-sn", "--sub_size", help="number of subpopulation", nargs='?', default=10, type=int)
    parser.add_argument(
        "-is",
        "--info_sharing",
        help="when to share info between subpops",
        nargs="+",
        default=None,
    )
    args = parser.parse_args()

    # TODO update lambda_ and mu_ arguments for subpopulation
    sigma0 = args.sigma0
    if args.subpop_type == 1:
        # no subpopulations, hard-coded size (hard-coded for now)
        lambda_ = [args.lambda_]
    elif args.subpop_type == 2:
        # no subpopulations, hard-coded size (hard-coded for now)
        lambda_ = [50, 50]
    elif args.subpop_type == 3:
        # multiple subpopulations, same sizes (hard-coded for now)
        lambda_ = [20, 20, 20, 20, 20]
    elif args.subpop_type == 4:
        # multiple subpopulations, same sizes (hard-coded for now)
        lambda_ = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
    elif args.subpop_type == 5:
        # multiple subpopulations, same sizes (hard-coded for now)
        lambda_ = [50, 10, 10, 10, 10, 10]
        sigma0 = [0.2, 0.05, 0.05, 0.05, 0.05, 0.05]

    print("Subpopulation CMA-ES: start")
    main(
        problem_id=args.problem_id,
        problem_instance=args.problem_instance,
        dimension=args.dimension,
        iterations=args.iterations,
        budget=int(args.budget * args.dimension),
        lambda_=lambda_,
        init_method=args.init_method,
        sigma0=sigma0,
        bound_corr=args.bound_corr,
        init_corr=args.init_corr,
        sharing=args.info_sharing,
        logger_info={"name": args.algo_name, "description": ""},
    )
    print("Subpopulation CMA-ES: complete")
    # python main.py -pt
