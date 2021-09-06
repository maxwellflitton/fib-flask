from flask import Flask

from data_access import dal
from fib_calcs import calc_fib_num
from fib_calcs.enums import CalculationMethod
from models.database.fib_entry import FibEntry
from task_queue.engine import make_celery
from rust_db_cloning import get_fib_enteries

app = Flask(__name__)
celery = make_celery(app)

from task_queue.fib_calc_task import create_calculate_fib
calculate_fib = create_calculate_fib(input_celery=celery)


@app.route("/")
def home():
    return "home for the fib calculator"


@app.route("/calculate/<int:number>")
def calculate(number):
    fib_calc = dal.session.query(FibEntry).filter_by(
                           input_number=number).one_or_none()
    if fib_calc is None:
        if number < 50:
            fib_number, time_taken = calc_fib_num(
                input_number=number,
                method=CalculationMethod.PYTHON
            )
            new_calc = FibEntry(input_number=number,
                                calculated_number=fib_number
                                )
            dal.session.add(new_calc)
            dal.session.commit()

            return f"you entered {number} " \
                   f"which has a Fibonacci number of " \
                   f"{fib_number} which took {time_taken}"
        calculate_fib.delay(number)
        return "calculate fib sent to queue because " \
               "it's above 30"
    return f"you entered {fib_calc.input_number} " \
           f"which has an existing Fibonacci number of " \
           f"{fib_calc.calculated_number}"


@app.route("/rust/calculate/<int:number>")
def rust_calculate(number):
    fib_calc = dal.session.query(FibEntry).filter_by(
                           input_number=number).one_or_none()
    if fib_calc is None:
        if number < 50:
            fib_number, time_taken = calc_fib_num(
                input_number=number,
                method=CalculationMethod.RUST
            )
            new_calc = FibEntry(input_number=number,
                                calculated_number=fib_number)
            dal.session.add(new_calc)
            dal.session.commit()

            return f"you entered {number} " \
                   f"which has a Fibonacci number of " \
                   f"{fib_number} which took {time_taken}"
        calculate_fib.delay(number)
        return "calculate fib sent to queue because " \
               "it's above 30"
    return f"you entered {fib_calc.input_number} " \
           f"which has an existing Fibonacci number of " \
           f"{fib_calc.calculated_number}"


@app.route("/get")
def get():
    return str(get_fib_enteries(dal.url))


@app.teardown_request
def teardown_request(*args, **kwargs):
    "Expire and remove the session after each request"
    dal.session.expire_all()
    dal.session.remove()
    dal.session.close()


if __name__ == "__main__":
    app.run(use_reloader=True, port=5002, threaded=True)
