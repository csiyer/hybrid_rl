/********* THINGS TO REVISIT
 * Feedback trial stimuli
 * testing everything
/*********/ 


/* Save experimental info */
experiment_id = jsPsych.randomization.randomID(20) // random subject ID of length 20
date = + new Date()
console.log('Experiment ID: ', experiment_id)

var subject_id = jsPsych.data.getURLVariable('PROLIFIC_PID');
var study_id = jsPsych.data.getURLVariable('STUDY_ID');
var session_id = jsPsych.data.getURLVariable('SESSION_ID');
console.log('Prolific info:', subject_id, study_id, session_id)

jsPsych.data.addProperties({
    experiment_id: experiment_id, //unique ID
    date: date, // current date
    // URL variables
    subject_id: subject_id,
    study_id: study_id,
    session_id: session_id,
  });

if (subject_id == undefined) {
    params.iteration = 'testing'
}
console.log('Iteration: ', params.iteration)

/*
    1. Initial checks
    2. Welcome & instructions
    3. Practice
    4. Task
    5. Debrief & finishing
    6. Run experiment
*/


/*** 1. Initial stuff ***/

var wrong_browser = { // if not using Chrome, prompt them to use chrome 
    type: 'html-keyboard-response',
    stimulus: 'Welcome! Please reopen this page in Chrome to begin the experiment.',
    choices: []
};

var local_alert = { // running non-local version?
    type: 'html-keyboard-response',
    stimulus: 'You are running this task locally! If you are a participant, please close this window and contact the experimenter.',
    choices: []
};

var iti = {
    type: 'html-keyboard-response',
    stimulus: '<div style="font-size:60px;">+</div>',
    choices: [],
    trial_duration: get_iti(),
    data: { trial_type: 'iti' }
};


/*** 2. Welcome & instructions ***/

var welcome_fullscreen = {
    type: 'fullscreen',
    message: "<p style= 'font-size:200%' ><b>Welcome to our experiment!</b></br></p>" + 
        "<p>The experiment will take approximately " + params.total_completion_time + " minute(s).</p><br><br>"+
        '<p>Before starting, please note that you are participating in a scientific study. Your responses are very important to us, and will be a huge help for our research.<br>' +
        'We ask that you give the study your full attention and best effort.<br>' +
        'Responding randomly, exiting full screen, or responding to only a few trials will lead your data to be rejected.<br>' +
        'We hope you choose to participate in our study!</p>'
        ,
    button_label: "Click to enter full screen and begin experiment",
    fullscreen_mode: true,
    on_start: function() {
        document.body.style.backgroundColor = params.background
        document.body.style.color = params.text_color
    }
}

var instructions = {
    type: instructions,
    pages: [
        "<p style='font-size:150%''><b>Consent Form</b></p>" + 
        "<p>Before we get started, feel free to take a look at our consent form, and download a copy for your records if you like:<p>" + 
        "<div style='padding:1%' >"  + 
        "<embed src='stimuli/online_consent.pdf' width='100%' height='400px' style='border: 2px solid lightgrey';/>" + 
        "</div>" + 
        "<p>Click 'Next' if you agree to participate and you will begin the experiment.</p>"
        ,  

        "<p style='font-size: 150%'><b>Instructions</b></p>" +
        "<p><img  style='width:30%'' src='stimuli/example-choice.png'></img>" +
        "<p>In this experiment, you will play a card came.</p>" +
        "<br>On each trial, you will pick between two cards, from an <b>orange deck</b> and a <b>blue deck</b>." +
        "<br>You will have " + params.choice_time / 1000 + " seconds to choose a card with the left (<b>&#x2190;</b>) and right (<b>&#x2192;</b>) arrow keys.</p>"
        ,

        "<p style='font-size: 150%'><b>Instructions</b></p>" +
        "<p><img  style='width:30%'' src='stimuli/example-feedback.png'></img>" +
        "<p>Your chosen card will then turn over, and you'll see how much it was worth.</p>" +
        "<p>Each card is worth between $0 and $1.</p>" +
        "<p>In this example, you chose the the card on the right (<b>&#x2192;</b>), which was worth <b>$1</b></p>." 
        ,

        "<p style='font-size: 150%'><b>Instructions</b></p>" +
        "<p><img  style='width:30%'' src='stimuli/example-feedback.png'></img>" +
        "<p>Your goal is to pick cards to make as much money as possible.</p>" +
        "<p>Your <b>real bonus</b> will be based on how much money you accumulate in the experiment!!</p>"
        ,

        "<p style='font-size: 150%'><b>Instructions</b></p>" +
        "<p><img  style='width:30%'' src='stimuli/example-trial.png'></img>" +
        "<p>There are two ways to maximize the amount of money you make in this experiment: </p>" +
        "<p>1. Sometimes you will encounter a <b>card you have chosen before</b>." + 
        "<br> These cards will always be worth the same amount as the first time you chose it," + 
        "<br> regardless of which deck it appears in the lucky or unlucky deck.</p>"+
        "<p><img  style='width:30%'' src='stimuli/example-old-card.png'></img>" +
        "<p>So, you can use your memory to pick cards that are worth more money.</p>"
        ,

        "<p style='font-size: 150%'><b>Instructions</b></p>" +
        "<p><img  style='width:30%'' src='stimuli/example-trial.png'></img>" +
        "<p>There are two ways to maximize the amount of money you make in this experiment: </p>" +
        "<p>2. In addition, at any point in the experiment, one of the decks is <b>\"lucky\"</b>." + 
        "<br> This means that this deck will tend to give good rewards." + 
        "<br> Here's an example of the difference in rewards between the lucky and unlucky decks:<br>"+
        "<p><img  style='width:30%'' src='stimuli/example-deck-values.png'></img>" +
        "<p> But, the lucky deck may switch at any point (between orange and blue)!</p>"+
        "<p><img  style='width:30%'' src='stimuli/example-deck-luck.png'></img>" +
        "<p>So, you can pick cards according to which deck you think is luckier at that point, and you will earn more.</p>"
        ,

        "<p style='font-size: 150%'><b>Instructions</b></p>" +
        "<p><img  style='width:30%'' src='stimuli/example-choice.png'></img>" +
        "<p>To review, you will see pairs of cards and select one with the left (<b>&#x2190;</b>) and right (<b>&#x2192;</b>) arrow keys.</p>" +
        "<p>You'll then see how much your card was worth, and you'll receive a final bonus proportionate to your total sum.</p>" +
        "<p>You can use (1) your memory, or (2) which deck you think is lucky at each point, to earn more money.</p>" 
        ,

        "<p style='font-size: 150%'><b>Instructions</b></p>" +
        "<p>When you press continue, you will begin a <b>brief practice period</b>.</p>" +
        "<p>Remember, select a card from the orange or blue deck with the <b>left (&#x2190;)</b> and <b>right (&#x2192;)</b> arrow keys.</p>" + 
        "<p>And remember to pay attention to the <b>lucky deck</p> and <b>repeated cards</b> to maximize your bonus!</p>"
    ],
    show_clickable_nav: true,
    show_page_number: false,
    post_trial_gap: 500,
    // on_finish: function() {
    //     document.body.style.backgroundColor = params.stim_background
    // }
}




/*** 3. Practice ***/
//n_pracitce_trials: 5
var practice_block = {

}

// detect if people just pick the same thing every single time or some filtering
var comprehension_check = {
    // quiz if they fail the practice
}  



/*** 4. Task ***/


// initialize deck lucks and deck placements randomly
if (Math.random () <= 0.5) {// initialize random which deck is lucky
    var deck_lucks = { blue: 'lucky', orange: 'unlucky'}
    var curr_lucky_deck = 'blue'
} else {
    var deck_lucks = { blue: 'unlucky', orange: 'lucky'}
    var curr_lucky_deck = 'orange'
}
if (Math.random () <= 0.5) {// initialize random which deck is lucky
    var deck_locs = { blue: 'left', orange: 'right'}
} else {
    var deck_locs = { blue: 'right', orange: 'left'}
}

// initialize outcomes (these will be reset each reversal) 
var outcomes = generate_outcomes()

// keep track of all objects we've already used
var possible_object_nums = [] 
for (var i = 1; i <= 665; i++) {
    possible_object_nums.push(i)
}
var old_object_nums_already_repeated = []

// keep track of data for the purpose of creating old trials
var old_trial_tracking = []
for (var i = 1; i <= params.n_trials_total; i++) {
    old_trial_tracking[i] = {
        'trial_number': NaN,
        'object': 'none',
        'value': NaN,
        'deck': 'none',
        'luck': 'none',
        'shown_twice': false,
    };
}

// keep track of average outcomes to keep values from inflating
var all_outcomes = []

// track trial numbers
var trial_number = 0
var block_number = 0
var trials_since_reversal = 0

// for each block
// generate reversals
// swap dec locations
// push trials
// push break 
// var ALL_BLOCK_TRIALS = []
// var reversals = get_block_reversals()


var choice = {
    type: "html-keyboard-response",
    stimulus: "",
    choices: ['ArrowLeft', 'ArrowRight'],
    trial_duration: params.choice_time,
    response_ends_trial: true,
    on_start: function (choice) {

        trial_number += 1;
        choice.data.trial_type = 'choice';
        choice.data.trial_number = trial_number;
        choice.data.block_number = block_number;
        choice.data.reversal_trial = 0;
        choice.data.lucky_deck = curr_lucky_deck,
        choice.data.blue_luck = deck_lucks['blue'];
        choice.data.orange_luck = deck_lucks['orange'];
        choice.data.blue_loc = deck_locs['blue'];
        choice.data.orange_loc = deck_locs['orange'];
        choice.data.old_trial = 0;

        if (params.randomize_deck_locs_per_trial) { // not currently using this
            if (Math.random() <= 0.5) {
                deck_locs = { blue: 'left', orange: 'right'};
            } else {
                deck_locs = { blue: 'right', orange: 'left'};
            }
            choice.data.blue_loc = deck_locs['blue'];
            choice.data.orange_loc = deck_locs['orange'];
        } 

        // First, is it a reversal? figure out which deck is lucky
        if (reversals.includes(trial_number)) {
            // swap the deck lucks
            [deck_lucks.blue, deck_lucks.orange] = [deck_lucks.orange, deck_lucks.blue]
            curr_lucky_deck = (curr_lucky_deck === 'blue') ? 'orange' : 'blue'; // swap
            trials_since_reversal = 0
            choice.data.reversal_trial = 1
            // regenerate outcomes for the upcoming reversal period
            outcomes = generate_outcomes()
        }
        choice.data.trials_since_reversal = trials_since_reversal
        trials_since_reversal += 1


        // Next, is this an old trial?
        if (Math.random() <= params.old_trial_proportion && trial_number > params.old_delay_min) {
            choice.data.old_trial = 1

            // our strategy will be to get candidate old trials and then select based on some criteria
            old_candidates = []
            min_back = trial_number - params.old_delay_min
            max_back = Math.max( trial_number - params.old_delay_max, 0)
            for (var i = max_back; i <= min_back; i++) {
                /* search for candidate old trials that
                    - have only been shown once
                    - a choice was made
                    - has a value that remains in the values we haven't sampled yet
                */
                if ( !old_trial_tracking[i]['shown_twice'] && ['blue','orange'].includes(old_trial_tracking[i]['deck']) ) {
                    // did it appear in the deck that is presently lucky or unlucky
                    var curr_luck = deck_lucks[ old_trial_tracking[i]['deck'] ]
                    // is the value remaining in the list of possible outcomes for this luck 
                    if (outcomes[curr_luck].includes(old_trial_tracking[i]['value'])) {
                        old_candidates.push(i)
                    }
                }
            }
            if (old_candidates.length > 0) {
                // we will prioritize objects that are incongruent with deck's expected value
                mismatch_old_candidates = []
                for (var i = 0; i < old_candidates.length; i++) {
                    candidate_i = old_candidates[i];
                    candidate_value = old_trial_tracking[candidate_i]['value'];
                    candidate_deck = old_trial_tracking[candidate_i]['deck'];
                    
                    if ( (candidate_deck == curr_lucky_deck && candidate_value < 0.5) || (candidate_deck != curr_lucky_deck && candidate_value > 0.5) ) {
                        mismatch_old_candidates.push(candidate_i);
                    }
                }

                if (mismatch_old_candidates.length > 0) { // choose the mismatches if we have them // MONITOR THIS FOR IF WE'RE ANTICORRELATING
                    old_candidates = mismatch_old_candidates;
                }
                // now choose an old object from the candidates
                // we also want to prioritize low-value objects *if* object values are on average really high
                if (array_average(all_outcomes) >= 0.5) {
                    ind_of_least_value = 0
                    least_value = 2
                    for (var j = 0; j < old_candidates.length; j++) {
                        if (old_trial_tracking[old_candidates[j]]['value'] < least_value) {
                            least_value = old_trial_tracking[old_candidates[j]]['value']
                            ind_of_least_value = j
                        }
                    }
                    old_object_trial = old_candidates[ind_of_least_value]
                } else {
                    old_object_trial = array_random_sample(old_candidates)
                }
                
                old_trial_tracking[old_object_trial]["shown_twice"] = true;
                choice.data.old_trial_number = old_trial_tracking[old_object_trial]["trial_number"];
                choice.data.old_deck = old_trial_tracking[old_object_trial]["deck"];
                choice.data.old_luck = old_trial_tracking[old_object_trial]["luck"];
                choice.data.old_value = old_trial_tracking[old_object_trial]["value"];
                choice.data.old_object = old_trial_tracking[old_object_trial]["object"];

                // remove old value from deck outcomes list
                const idx_of_value = outcomes[deck_lucks[choice.data.old_deck]].indexOf(choice.data.old_value)
                outcomes[deck_lucks[choice.data.old_deck]].splice(idx_of_value, 1)

                // assign the stimuli 
                var rand_idx = get_random_index(possible_object_nums) // get a random object
                var new_object = possible_object_nums[rand_idx] 
                possible_object_nums.splice(rand_idx, 1) // remove it from array of possible objects

                if (choice.data.old_deck == 'blue') {
                    choice.data.blue_object = choice.data.old_object
                    choice.data.blue_value = choice.data.old_value
                    choice.data.orange_object = new_object
                    choice.data.orange_value = outcomes[deck_lucks['orange']].shift()
                } else {
                    choice.data.orange_object = choice.data.old_object
                    choice.data.orange_value = choice.data.old_value
                    choice.data.blue_object = new_object
                    choice.data.blue_value = outcomes[deck_lucks['blue']].shift()
                }

            } else {
                // failed to find old object, treat as a new/new trial -- this should be rare!!!!
                console.log('Failed to find old object, trial ' + trial_number)
                choice.data.old_trial = 0

                rand_idx = get_random_index(possible_object_nums) // get a random object
                choice.data.blue_object = possible_object_nums[rand_idx]
                possible_object_nums.splice(rand_idx, 1) // remove it from array of possible objects
                choice.data.blue_value = outcomes[deck_lucks['blue']].shift() // remove first element and its the value

                rand_idx = get_random_index(possible_object_nums)
                choice.data.orange_object = possible_object_nums[rand_idx]
                possible_object_nums.splice(rand_idx, 1)
                choice.data.orange_value = outcomes[deck_lucks['orange']].shift()
            }
           
        } else { // new/new trial 
            rand_idx = get_random_index(possible_object_nums) // get a random object
            choice.data.blue_object = possible_object_nums[rand_idx]
            possible_object_nums.splice(rand_idx, 1) // remove it from array of possible objects
            choice.data.blue_value = outcomes[deck_lucks['blue']].shift() // remove first element and its the value

            rand_idx = get_random_index(possible_object_nums)
            choice.data.orange_object = possible_object_nums[rand_idx]
            possible_object_nums.splice(rand_idx, 1)
            choice.data.orange_value = outcomes[deck_lucks['orange']].shift()
        }

        // Finally, assign the stimuli to right/left and embed
        if (deck_locs['blue'] == 'left') {
            left_stim = "stimuli/blue/object" + trial_data.blue_object + ".jpg"
            right_stim =  "stimuli/orange/object" + trial_data.orange_object + ".jpg"
            choice.data.left_value = choice.data.blue_value
            choice.data.left_object = choice.data.blue_object
            choice.data.right_value = choice.data.orange_value
            choice.data.right_object = choice.data.orange_object
        } else {
            left_stim = "stimuli/orange/object" + trial_data.orange_object + ".jpg"
            right_stim =  "stimuli/blue/object" + trial_data.blue_object + ".jpg"
            choice.data.left_value = choice.data.orange_value
            choice.data.left_object = choice.data.orange_object
            choice.data.right_value = choice.data.blue_value
            choice.data.right_object = choice.data.blue_object
        }
        choice.stimulus = "<div style='width: 800px;'>" +
            "<div style='float: left;'><img src='" + left_stim + "'></img></div>" +
            "<div style='float: right;'><img src='" + right_stim + "'></img></div>" +
            "</div>"
    },
    on_finish: function(data) {

        if (['ArrowLeft','ArrowRight'].includes(data.response)) {
            
            if (data.response=="ArrowLeft") {
                data.left_chosen = 1
                if (data.blue_loc == 'left') {
                    data.blue_chosen = 1
                    data.deck_chosen = 'blue'
                    data.object_chosen = data.blue_object
                    data.outcome = data.blue_value
                } else {
                    data.blue_chosen = 0
                    data.deck_chosen = 'orange'
                    data.object_chosen = data.orange_object
                    data.outcome = data.orange_value
                }
            } else if (data.response == 'ArrowRight') {
                data.left_chosen = 0
                if (data.blue_loc == 'right') {
                    data.blue_chosen = 1
                    data.deck_chosen = 'blue'
                    data.object_chosen = data.blue_object
                    data.outcome = data.blue_value
                } else {
                    data.blue_chosen = 0
                    data.deck_chosen = 'orange'
                    data.object_chosen = data.orange_object
                    data.outcome = data.orange_value
                }
            }
            data.lucky_chosen = + data.deck_chosen == data.lucky_deck

            if (data.old_trial == 1 && ['blue','orange'].includes(data.deck_chosen)) {
                data.old_chosen = + data.deck_chosen == data.old_deck
                data.optimal_old_choice = + ( (data.old_chosen==0 && data.old_value < 0.5 ) || (data.old_chosen==1 && data.old_value>0.5) )
            }
            
            all_outcomes.push(data.outcome) // for keeping track of average value of all feedback over time

        } else {
            data.deck_chosen = 'no_response'
        }

        // update the old_trial_tracking variables
        old_trial_tracking[trial_number]['trial_number'] = data.trial_number;
        old_trial_tracking[trial_number]['value'] = data.outcome;
        old_trial_tracking[trial_number]['deck'] = data.deck_chosen;
        old_trial_tracking[trial_number]['object'] = data.object_chosen;
        if (data.old_chosen) { old_trial_tracking[trial_number]["shown_twice"] = true }
        if (data.lucky_chosen) {
            old_trial_tracking[trial_number]['luck'] = "lucky";
        } else {
            old_trial_tracking[trial_number]['luck'] = "unlucky";
        }
    }
};


// choice confirmation just puts a green box around the chosen item until the end of the trial
var choice_confirmation = {
    type: 'html-keyboard-response',
    stimulus: function () {
        if (jsPsych.data.get().last(1).values()[0].deck_chosen == "no_response") {
            return '' // 0 trial duration anyways, just skip 
        } else {
            if (jsPsych.data.get().last(1).values()[0].left_chosen == 1;) {
                document.body.style.background = "url('stimuli/blank_confirmation_left.jpg') no-repeat center center";
            } else {
                document.body.style.background = "url('stimuli/blank_confirmation_right.jpg') no-repeat center center";
            }
        }
        return jsPsych.data.get().last(1).values()[0].stimulus;
    },
    choices: [],
    trial_duration: function () { // until the end of the trial
        if (jsPsych.data.get().last(1).values()[0].deck_chosen == "no_response") {
            return 0 
        } else {
            return (params.choice_time - jsPsych.data.get().last(1).values()[0].rt;);
        }
    },
    data: { trial_type: 'confirmation' }
};


// feedback portion will show the value of the chosen card
var feedback = {
    type: 'html-keyboard-response',
    stimulus: function () {
        document.body.style.background = "url('stimuli/blank_background.jpg') no-repeat center center";

        var last_trial_earned = jsPsych.data.get().last(2).values()[0].outcome;
        var left_chosen = jsPsych.data.get().last(2).values()[0].left_chosen;
        var stim = jsPsych.data.get().last(2).values()[0].stimulus;
        var choice = jsPsych.data.get().last(2).values()[0].deck_chosen;
        var blue_left = jsPsych.data.get().last(2).values()[0].blue_left;

        if (blue_left) {
            leftImg = "blue/";
            rightImg = "orange/";
        } else if (!blue_left) {
            leftImg = "orange/";
            rightImg = "blue/";
        }

        if (last_trial_earned == 0) {
            imgVal = "0.jpg"
        } else if (last_trial_earned == 0.2) {
            imgVal = "20.jpg"
        } else if (last_trial_earned == 0.4) {
            imgVal = "40.jpg"
        } else if (last_trial_earned == 0.6) {
            imgVal = "60.jpg"
        } else if (last_trial_earned == 0.8) {
            imgVal = "80.jpg"
        } else if (last_trial_earned == 1) {
            imgVal = "1.jpg"
        }

        stim_array = stim.split('stimuli/')
        out_stim = stim_array[0]
        for (i = 1; i < stim_array.length; i++) {
            imgName = stim_array[i].split('></stimuli')[0]
            imgNames = imgName.split('.')
            
            if (left_chosen) {
                // only replace the left image
                if (i == 1) {
                    out_stim = out_stim + "stimuli/feedback/" + leftImg + imgVal + "'" + '></stimuli' + stim_array[i].split('></stimuli')[1]
                } else {
                    out_stim = out_stim + "stimuli/feedback/" + "blank.jpg" + "'" + '></stimuli' + stim_array[i].split('></stimuli')[1]
                }
            } else if (choice != "no_response") {
                // only replace the right image
                if (i == 2) {
                    out_stim = out_stim + "stimuli/feedback/" + rightImg + imgVal + "'" + '></stimuli' + stim_array[i].split('></img')[1]
                } else {
                    out_stim = out_stim + "stimuli/feedback/" + "blank.jpg" + "'" + '></stimuli' + stim_array[i].split('></img')[1]
                }
            } else if (choice == "no_response") {
                out_stim = '<div style="font-size:60px;">Too Slow!</div>';
            }
        }
        return out_stim
    },
    choices: [],
    trial_duration: params.feedback_time,
    data: { trial_type: 'feedback' }
};


var block_break = {
    type: 'html-button-response',
    stimulus:  "<p style='font-size: 150%'><b>Take a break!</b></p>" +
        "<p>Take up to 2 minutes, and press 'Continue' when you're ready to begin again.</p>" +
    choices: ['Continue'],
    trial_duration: [120000],
}


var practice_procedure = {
    timeline: [fixation, practice_choice, choice_confirmation, feedback],
    timeline_variables: [{ stimulus: "", data: {} }];
    repetitions: params.n_practice_trials
};

var main_procedure = {
    timeline: [iti, choice, choice_confirmation, feedback],
    timeline_variables: [{ stimulus: "", data: {} }];
    repetitions: params.n_trials_per_block
}


/*** 5. Debrief & finishing ***/

var debrief_block = {
    type: "html-button-response",
    stimulus: function () {
        
        var feedback_trials = jsPsych.data.get().filter({ trial_type: 'feedback' });
        bonus = feedback_trials.select('outcome').sum() * params.bonus_downweighting, 2
        bonus = max(bonus, params.max_bonus).toFixed(2)

        var choice_trials = jsPsych.data.get().filter({ trial_type: 'choice' });
        var choice_trials_old = choice_trials.filter({old_trial: 1})
        var choice_trials_old_optimal = choice_trials_old.filter({optimal_old_choice: 1})
        rt = Math.round(choice_trials.select('rt').mean());
        accuracy = Math.round(choice_trials_old_optimal.count() / choice_trials_old.count() * 100)

        time_elapsed = (jsPsych.data.getLastTrialData().values()[0].time_elapsed / 1000 / 60).toFixed(2)

        return "<p>You earned a total bonus of <b>$" + bonus + "</b>!</p>" +
            "<p>Your average response time was " + rt + "ms.</p>" +
            "<p>You correctly remembered " + accuracy + "% of repeated images."
    },
    choices: ['Save data and end experiment'],
    response_ends_trial: true,
    on_finish:  function(data) {
        data.params = params
        data.trial_type = 'summary'
        data.experimental_duration = time_elapsed
        data.bonus = bonus
        data.total_payment = bonus + params.base_pay
        data.mean_rt = rt
        data.accuracy = accuracy
        data.experiment_id = experiment_id
        data.datetime = new Date().toLocaleString();
        console.log('Summary data:', data)
    }
}

var fullscreen_close = {
    type: 'fullscreen',
    fullscreen_mode:false,
}

var end_screen = {
    type: 'html-keyboard-response',
    stimulus: '<p>Thank you for completing the experiment! Press any key to be redirected back to Prolific.</p>',
    response_ends_trial: true
}



/*** 6. Populate timeline and run experiment ***/

if (get_browser_type() != 'Chrome') {
	timeline.push(wrong_browser)
}
if (params.local) {
    timeline.push(local_alert)
}

timeline.push(welcome_fullscreen, instructions)
// task in here
timeline.push(debrief_block, fullscreen_close, end_screen)


// preload images
all_images = [
    'stimuli/online_consent.pdf',
    'stimuli/example-choice.png',
    'stimuli/example-feedback.png',
    'stimuli/example-trial.png',
    'stimuli/example-deck-values.png',
    'stimuli/example-deck-luck.png',
    'stimuli/blank_confirmation_left.jpg',
    'stimuli/blank_confirmation_right.jpg',
    'stimuli/blank_background.jpg'
]
// card images
for (var i = 1; i <= 665; i++) {
    images.push('stimuli/blue/object' + i + '.jpg')
    images.push('stimuli/orange/object' + i + '.jpg')
    // images.push('stimuli/no_deck/object' + i + '.jpg')
}
// feedback images
vals = ["0.jpg", "20.jpg", "40.jpg", "60.jpg", "80.jpg", "1.jpg"];
for (var i = 0; i < vals.length; i++) {
    images.push('stimuli/feedback/blue/'+vals[i])
    images.push('stimuli/feedback/orange/'+vals[i])
    //images.push('stimuli/feedback/no_deck/'+vals[i])
    images.push('stimuli/feedback/blank.jpg')
}


jsPsych.init({
    timeline: timeline,
    preload_images: all_images,
    exclusions: {
        min_width: 1350,
        min_height: 759
    },
    on_finish: function() {
      window.location = params.prolific_redirect_link
    }
});

