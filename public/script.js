const socket = io();

socket.on("connect", () => {
  //console.log(socket.id);
});

socket.on("information", (payload) => {
  const { status, deadline } = payload;

  const Scoreboard = React.createClass({
    getInitialState: function () {
      return payload;
    },

    onScoreChange: function (index, delta) {
      this.state.candidates[index].score += delta;
      this.setState(this.state);
    },

    render: function () {
      return (
        <div className="scoreboard">
          <Header candidates={this.state.candidates} />
          <div className="candidates">
            {this.state.candidates.map(
              function (player, index) {
                return (
                  <Player
                    name={player.name}
                    vote={player.vote}
                    key={player.name}
                    onScoreChange={(delta) => this.onScoreChange(index, delta)}
                  />
                );
              }.bind(this)
            )}
          </div>
        </div>
      );
    },
  });

  function Header(props) {
    return (
      <div className="header">
        <Stats candidates={props.candidates} />
        <h1>جدول آراء</h1>
        <Stopwatch />
      </div>
    );
  }

  Header.propTypes = {
    candidates: React.PropTypes.array.isRequired,
  };

  function Stats(props) {
    const playerCount = props.candidates.length;
    const totalPoints = props.candidates.reduce(function (total, player) {
      return total + player.vote;
    }, 0);

    return (
      <table className="stats">
        <tbody>
          <tr>
            <td>تعداد کاندیدها:</td>
            <td>{playerCount}</td>
          </tr>
          <tr>
            <td>مجموع آراء:</td>
            <td>{totalPoints}</td>
          </tr>
        </tbody>
      </table>
    );
  }

  Stats.propTypes = {
    candidates: React.PropTypes.array.isRequired,
  };

  function refreshTime() {
    var now = new Date();
    var result =
      ("0" + (deadline - now.getHours())).slice(-2) +
      ":" +
      ("0" + (59 - now.getMinutes())).slice(-2) +
      ":" +
      ("0" + (60 - now.getSeconds())).slice(-2);
    return result;
  }

  const Stopwatch = React.createClass({
    render: function () {
      return (
        <div className="stopwatch">
          <h2>زمان باقی‌مانده برای رأی دادن</h2>
          <div className="stopwatch-time" id="stopwatch">
            {refreshTime()}
          </div>
        </div>
      );
    },
  });

  function Player(props) {
    return (
      <div className="player">
        <div className="player-name">{props.name}</div>
        <div className="player-score">
          <Counter vote={props.vote} />
        </div>
      </div>
    );
  }

  Player.propTypes = {
    name: React.PropTypes.string.isRequired,
    vote: React.PropTypes.number.isRequired,
    onScoreChange: React.PropTypes.func.isRequired,
  };

  function Counter(props) {
    return (
      <div className="counter">
        <div className="counter-score">{props.vote}</div>
      </div>
    );
  }

  Counter.propTypes = {
    onChange: React.PropTypes.func.isRequired,
    vote: React.PropTypes.number.isRequired,
  };

  ReactDOM.render(<Scoreboard />, document.getElementById("root"));

  var timeDisplay = document.getElementById("stopwatch");

  function update() {
    timeDisplay.innerHTML = refreshTime();
  }

  setInterval(update, 1000);
});
